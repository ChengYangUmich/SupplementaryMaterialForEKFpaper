import ctypes
from ctypes import POINTER, CFUNCTYPE
from ctypes import c_double, c_int, c_uint, c_short
from ctypes import c_char, c_char_p, c_longlong, c_ulonglong
from time import time
from time import sleep
import os
import os.path
import zipfile
import tempfile
import shutil
import platform
import sys

class C_sumo_handle(ctypes.Structure):
  pass

class _Duration:
	"""Data structure to hold duration constants."""
	pass

dur = _Duration()

dur.msec = 1
dur.sec  = 1000 * dur.msec
dur.min  = 60 * dur.sec
dur.hour = 60 * dur.min
dur.day  = 24 * dur.hour

class Sumo:
    def __init__(self, sumoPath, licenseFile):
        self.version = '15.11.2019'
        self.sumoPath = sumoPath
        self.licenseFile = licenseFile
        self.platform_name = ''
        self.library_prefix = ''
        self.library_ext = ''
        self.simulation_finished = False
        self.script_loaded = False
        self.model_loaded = False
        self.model_initialized = False

        self.datacomm_callback = None
        self.message_callback = None
        self.simulation_finished_callback = None

        self.messages = []

        # loading the Sumo core
        self.platform_name = platform.system()
        if self.platform_name == 'Windows':
            self.library_ext = 'dll'
            self.library_prefix = ''
            if sys.version_info[0] > 3 or (sys.version_info[0] == 3 and sys.version_info[1] >= 8):
                os.add_dll_directory(self.sumoPath) # Python 3.8
        elif self.platform_name == 'Linux':
            self.library_ext = 'so'
            self.library_prefix = 'lib'
        elif self.platform_name == 'Darwin':
            self.library_ext = 'dylib'
            self.library_prefix = 'lib'
        else:
            raise NotImplementedError('Unsupported platform.')

        core_filename = os.path.join(self.sumoPath, self.library_prefix + "sumocore." + self.library_ext)
        if os.path.isfile(core_filename):
            cwd = os.getcwd()
            os.chdir(self.sumoPath)
            self.core = ctypes.cdll.LoadLibrary(core_filename)
            os.chdir(cwd)
        else:
            raise FileNotFoundError('Core file not found: ' + core_filename)

        # --------------------------------------------------------------------------------------------
        # structures and configuration needed by ctypes to use exported functions correctly
        # restype: result type (return type)
        # argtypes: argument types
        # --------------------------------------------------------------------------------------------

        self.core.csumo_create.restype = POINTER(C_sumo_handle)

        self.core.csumo_destroy.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_wait_for_finished.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_force_quit.argtypes = [POINTER(C_sumo_handle)]

        self.core.csumo_model_load.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_model_load.restype = c_int

        self.core.csumo_model_unload.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_model_unload.restype = c_int

        self.core.csumo_model_name_get.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_model_name_get.restype = c_char_p

        self.core.csumo_start_core_session.argtypes = [POINTER(C_sumo_handle), ctypes.c_short]

        self.core.csumo_datacomm_callback_register.argtypes = [POINTER(C_sumo_handle), CFUNCTYPE(c_int, POINTER(C_sumo_handle))]

        self.core.csumo_datacomm_simulation_finished_register.argtypes = [POINTER(C_sumo_handle), CFUNCTYPE(c_int, POINTER(C_sumo_handle))]
        self.core.csumo_message_callback_register.argtypes = [POINTER(C_sumo_handle), CFUNCTYPE(c_int, POINTER(C_sumo_handle))]
        self.core.csumo_error_callback_register.argtypes = [POINTER(C_sumo_handle), CFUNCTYPE(c_int, POINTER(C_sumo_handle))]

        self.core.csumo_error_get_details.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_error_get_details.restype = c_char_p

        self.core.csumo_set_initial_mode.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_get_mode.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_get_mode.restype = c_char_p

        self.core.csumo_get_stepCount.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_get_stepCount.restype = c_longlong

        #
        # These calls below should be used only in callback functions otherwise
        # the returned values might be out of sync, or in some extreme situations
        # can be garbage as well.
        #
        self.core.csumo_var_get_pvt.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_var_get_pvt.restype = c_double
        self.core.csumo_var_get_int.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_var_get_int.restype = c_longlong
        self.core.csumo_var_get_bool.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_var_get_bool.restype = c_short
        self.core.csumo_var_get_string.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_var_get_string.restype = c_char_p
        self.core.csumo_var_get_pvtarray.argtypes = [POINTER(C_sumo_handle), c_char_p, c_int]
        self.core.csumo_var_get_pvtarray.restype = c_double
        self.core.csumo_var_get_pvtarray_size.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_var_get_pvtarray_size.restype = c_int

        #
        # Accessing variables via positions. The respective positions can be
        # retrieved by the csumo_model_get_variable_info_pos call (see below).
        # Getters first:
        #
        self.core.csumo_var_get_pvt_pos.argtypes = [POINTER(C_sumo_handle), c_int]
        self.core.csumo_var_get_pvt_pos.restype = c_double
        self.core.csumo_var_get_int_pos.argtypes = [POINTER(C_sumo_handle), c_int]
        self.core.csumo_var_get_int_pos.restype = c_longlong
        self.core.csumo_var_get_bool_pos.argtypes = [POINTER(C_sumo_handle), c_int]
        self.core.csumo_var_get_bool_pos.restype = c_short
        self.core.csumo_var_get_string_pos.argtypes = [POINTER(C_sumo_handle), c_int]
        self.core.csumo_var_get_string_pos.restype = c_char_p
        self.core.csumo_var_get_pvtarray_pos.argtypes = [POINTER(C_sumo_handle), c_int, c_int]
        self.core.csumo_var_get_pvtarray_pos.restype = c_double
        self.core.csumo_var_get_pvtarray_size_pos.argtypes = [POINTER(C_sumo_handle), c_int, c_int]
        self.core.csumo_var_get_pvtarray_size_pos.restype = c_int

        #
        # Then setters:
        #
        self.core.csumo_var_set_pvt_pos.argtypes = [POINTER(C_sumo_handle), c_int, c_double]
        self.core.csumo_var_set_int_pos.argtypes = [POINTER(C_sumo_handle), c_int, c_longlong]
        self.core.csumo_var_set_bool_pos.argtypes = [POINTER(C_sumo_handle), c_int, c_short]
        self.core.csumo_var_set_pvtarray_pos.argtypes = [POINTER(C_sumo_handle), c_int, c_int, c_double]

        #
        # General calls, returning data in string format
        #
        self.core.csumo_var_get.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_var_get.restype = c_char_p
        self.core.csumo_get_state_variables.argtypes = [POINTER(C_sumo_handle), c_char]
        self.core.csumo_get_state_variables.restype = c_char_p

        #
        # Dimension variables
        #
        self.core.csumo_var_get_dimension_variables.argtypes = [POINTER(C_sumo_handle), c_char_p, c_char]
        self.core.csumo_var_get_dimension_variables.restype = c_char_p

        #
        # Querying time in days
        #
        self.core.csumo_var_get_time_double.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_var_get_time_double.restype = c_double

        #
        # Querying time in milliseconds
        #
        self.core.csumo_var_get_time_int.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_var_get_time_int.restype = c_ulonglong

        #
        # Querying step sizes in milliseconds
        #
        self.core.csumo_var_get_dt_int.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_var_get_dt_int.restype = c_longlong

        #
        # Sending commands
        #
        self.core.csumo_command_send.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_command_send_blocking.argtypes = [POINTER(C_sumo_handle), c_char_p]

        #
        # Message handling
        #
        self.core.csumo_messages_get_last.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_messages_get_last.restype = c_char_p

        self.core.csumo_messages_get_all.argtypes = [POINTER(C_sumo_handle), c_char]
        self.core.csumo_messages_get_all.restype = c_char_p
        
        #
        # Variable pool queries
        #
        self.core.csumo_get_variables.argtypes = [POINTER(C_sumo_handle), c_char]
        self.core.csumo_get_variables.restype = c_char_p
        self.core.csumo_get_variables_types.argtypes = [POINTER(C_sumo_handle), POINTER(c_int)]
        # TODO: self.core.csumo_get_variables_types.restype = TODO
        self.core.csumo_get_variables_sumosymbol.argtypes = [POINTER(C_sumo_handle), c_char]
        self.core.csumo_get_variables_sumosymbol.restype = c_char_p

        # 
        # Individual variables properties
        #
        self.core.csumo_model_get_variable_info.argtypes = [POINTER(C_sumo_handle), c_char_p]
        # TODO: self.core.csumo_model_get_variable_info.restype = TODO
        self.core.csumo_model_get_variable_info_pos.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_model_get_variable_info_pos.restype = c_int
        self.core.csumo_model_get_variable_info_xmlpos.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_model_get_variable_info_xmlpos.restype = c_int
        self.core.csumo_model_get_variable_info_type.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_model_get_variable_info_type.restype = c_char_p
        self.core.csumo_model_get_variable_info_namespace.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_model_get_variable_info_namespace.restype = c_char_p
        self.core.csumo_model_get_variable_info_unit.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_model_get_variable_info_unit.restype = c_char_p
        self.core.csumo_model_get_variable_info_formatstring.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_model_get_variable_info_formatstring.restype = c_char_p

        self.core.csumo_var_get_sumosymbol.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_var_get_sumosymbol.restype = c_char_p
        self.core.csumo_var_get_sumosymbol_pos.argtypes = [POINTER(C_sumo_handle), c_int]
        self.core.csumo_var_get_sumosymbol_pos.restype = c_char_p     

        #
        # Variable focus, follow, show - this is not something you typically use...
        #   
        self.core.csumo_focus_get.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_focus_get.restype = c_char_p
        self.core.csumo_follow_get.argtypes = [POINTER(C_sumo_handle), c_char]
        self.core.csumo_follow_get.restype = c_char_p
        self.core.csumo_show_get.argtypes = [POINTER(C_sumo_handle), c_char]
        self.core.csumo_show_get.restype = c_char_p

        #
        # Model execution
        #
        self.core.csumo_status_simulation_finished.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_status_simulation_finished.restype = c_short

        #
        # Licensing
        #
        self.core.csumo_license_is_valid.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_license_is_valid.restype = c_short
        self.core.csumo_license_is_valid_code.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_license_is_valid_code.restype = c_short
        self.core.csumo_license_is_valid_details.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_license_is_valid_details.restype = c_char_p
        self.core.csumo_license_get_errorcode.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_license_get_errorcode.restype = c_int
        self.core.csumo_license_machine_identification_code.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_license_machine_identification_code.restype = c_char_p
        self.core.csumo_license_get_startdate.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_license_get_startdate.restype = c_char_p
        self.core.csumo_license_get_enddate.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_license_get_enddate.restype = c_char_p
        self.core.csumo_license_get_licensetype.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_license_get_licensetype.restype = c_char_p
        self.core.csumo_license_is_active.argtypes = [POINTER(C_sumo_handle)]
        self.core.csumo_license_is_active.restype = c_int
        self.core.csumo_license_update_dongle.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_license_update_dongle.restype = c_int
        self.core.csumo_license_update_dongle_code.argtypes = [POINTER(C_sumo_handle), c_char_p]
        self.core.csumo_license_update_dongle_code.restype = c_int
        self.core.csumo_license_retrieve_current_from_system.argtypes = []
        self.core.csumo_license_retrieve_current_from_system.restype = c_char_p
        self.core.csumo_license_retrieve_details_from_current_license.argtypes = [c_char]
        self.core.csumo_license_retrieve_details_from_current_license.restype = c_char_p

        def internal_datacomm_callback(handle):
            if self.datacomm_callback is not None:
                return self.datacomm_callback(self)
            else:
                return 0

        def internal_message_callback(handle):
            m = self.core.csumo_messages_get_all(handle, b';')

            if m is not None:
                for i in m.decode('utf8').split(';'):
                    if '530036' in i: self.script_loaded = True
                    if '530049' in i: self.model_initialized = True
                    if '530004' in i: self.simulation_finished = True
                    self.messages.append(i)
            if self.message_callback is not None:
                return self.message_callback(self)
            else:
                return 0

        def internal_simulation_finished_callback(handle):
            self.simulation_finished = True
            if self.simulation_finished_callback is not None:
                return self.simulation_finished_callback(self)
            else:
                return 0

        CALLBACKFUNC = ctypes.CFUNCTYPE(c_int, POINTER(C_sumo_handle))

        self.c_datacomm_callback = CALLBACKFUNC(internal_datacomm_callback)
        self.c_message_callback = CALLBACKFUNC(internal_message_callback)
        self.c_simulation_finished_callback = CALLBACKFUNC(internal_simulation_finished_callback)

        # so let's start the engine...
        self.handle = self.core.csumo_create()
        if not self.core.csumo_license_is_valid(self.handle, self.licenseFile.encode('utf8')):
            print("License not valid. Please contact Dynamita for a valid license.")
            print("Your machine identification code is: " + self.core.csumo_license_machine_identification_code(self.handle).decode('utf8'))
            print("Send them the code, they will need it.")
            exit()
        else:
            print("License OK...")

    def load_model(self, project_name):
        if self.model_loaded:
            print('A model is already loaded. Unload it before loading the next one.')
            return -1

        model_name = ''
        if project_name.endswith(".sumo"):
            self.tempdir = tempfile.mkdtemp()
            project = zipfile.ZipFile(project_name, 'r')
            project.extractall(self.tempdir)
            project.close()
            model_name = os.path.join(self.tempdir, 'sumoproject.dll').encode('utf8')
        else:
            model_name = project_name.encode('utf8')

        print("Trying to load model:", model_name)
        load_result = self.core.csumo_model_load(self.handle, model_name)
        if load_result != 0:
            print('Error during model load...')
            return load_result

        self.core.csumo_datacomm_callback_register(self.handle, self.c_datacomm_callback)
        self.core.csumo_message_callback_register(self.handle, self.c_message_callback)
        self.core.csumo_datacomm_simulation_finished_register(self.handle, self.c_simulation_finished_callback)

        self.core.csumo_start_core_session(self.handle, 1)

        while not self.model_initialized:
            sleep(1)

        self.model_loaded = True
        return load_result
		
    def unload_model(self):
        if not self.model_loaded:
            print('No model is loaded')
            return
        self.core.csumo_model_unload(self.handle)
        if self.platform_name == 'Windows':
            sleep(1)
            shutil.rmtree(self.tempdir)
        self.model_loaded = False

    def run_model(self):
        if not self.model_loaded:
            print('No model loaded')
            return
        self.simulation_finished = False
        self.core.csumo_command_send(self.handle, b"start;")

    def set_stopTime(self, stopTime):
        if not self.model_loaded:
            print('No model loaded')
            return
        stopTimeCommand = 'set Sumo__StopTime ' + str(stopTime) + ';'
        self.core.csumo_command_send(self.handle, stopTimeCommand.encode('utf8'))

    def set_dataComm(self, dataComm):
        if not self.model_loaded:
            print('No model loaded')
            return
        dataCommCommand = 'set Sumo__DataComm ' + str(dataComm) + ';'
        self.core.csumo_command_send(self.handle, dataCommCommand.encode('utf8'))

    def register_datacomm_callback(self, datacomm_callback):
        self.datacomm_callback = datacomm_callback

    def register_message_callback(self, message_callback):
        self.message_callback = message_callback

    def register_simulation_finished_callback(self, simulation_finished_callback):
        self.simulation_finished_callback = simulation_finished_callback
        
    def send_command(self, command):
        self.core.csumo_command_send(self.handle, command.encode('utf8'))