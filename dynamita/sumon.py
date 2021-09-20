import ctypes
import time
import os
import zipfile
import tempfile
import shutil
import platform
import sys

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
        # Preparing some convenience member fields.
        self.version = 'Sumo20'
        self.platform_name = ''
        self.simulation_finished = False
        self.script_loaded = False
        self.model_loaded = False
        self.model_initialized = False

        self.datacomm_callback = None
        self.message_callback = None
        self.simulation_finished_callback = None

        self.messages = []

        self._load_sumo(sumoPath)
        self._setup_C_API()
        self._create_core(licenseFile)


    def _load_sumo(self, sumoPath):
        library_prefix = ''
        library_ext = ''
        self.platform_name = platform.system()
        if self.platform_name == 'Windows':
            library_ext = 'dll'
            library_prefix = ''
            if sys.version_info[0] > 3 or (sys.version_info[0] == 3 and sys.version_info[1] >= 8):
                os.add_dll_directory(sumoPath) # Python 3.8
        elif self.platform_name == 'Linux':
            library_ext = 'so'
            library_prefix = 'lib'
        elif self.platform_name == 'Darwin':
            library_ext = 'dylib'
            library_prefix = 'lib'
        else:
            raise NotImplementedError('Unsupported platform.')

        core_filename = os.path.join(
            sumoPath, library_prefix + "sumocore." + library_ext
        )
        if os.path.isfile(core_filename):
            cwd = os.getcwd()
            os.chdir(sumoPath)
            self.core = ctypes.cdll.LoadLibrary(core_filename)
            os.chdir(cwd)
        else:
            raise FileNotFoundError('Core file not found: ' + core_filename)


    def _create_core(self, licenseFile):
        # Create and initialise the Sumo core.
        self.core.csumon_create()
        if 0 != self.core.csumon_use_license(
            licenseFile.encode('utf8')
        ):
            print(
                "License not valid. Please contact Dynamita for a valid license."
            )
            print(
                "Your machine identification code is:",
                self.machine_identification_code()
            )
            print("Send them the code, they will need it.")
            exit()
        else:
            print("License OK...")


    # Note1: the C functions with void return value and empty argument
    # list are not mentioned in this setup method.
    # Note2: the restype of allocated strings will be c_void_p, instead of
    # c_char_p, to be able to use the pointer in csumon_free.
    def _setup_C_API(self):
        self.core.csumon_load_model.argtypes = \
            [ctypes.c_char_p]
        self.core.csumon_load_model.restype = \
            ctypes.c_int

        self.core.csumon_unload_model.restype = \
            ctypes.c_int

        self.core.csumon_register_datacomm_cb.argtypes = \
            [ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)]

        self.core.csumon_register_simulation_finished_cb.argtypes = \
            [ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)]

        self.core.csumon_register_message_cb.argtypes = \
            [ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)]

        # The error registration API is for C client programs.

        self.core.csumon_set_mode.argtypes = \
            [ctypes.c_char_p]

        self.core.csumon_real.argtypes = \
            [ctypes.c_char_p]
        self.core.csumon_real.restype = \
            ctypes.c_double

        self.core.csumon_int.argtypes = \
            [ctypes.c_char_p]
        self.core.csumon_int.restype = \
            ctypes.c_longlong

        self.core.csumon_bool.argtypes = \
            [ctypes.c_char_p]
        self.core.csumon_bool.restype = \
            ctypes.c_short

        self.core.csumon_string.argtypes = \
            [ctypes.c_char_p]
        # Note c_void_p instead of c_char_p.
        self.core.csumon_string.restype = \
            ctypes.c_void_p

        self.core.csumon_array_size.argtypes = \
            [ctypes.c_char_p]
        self.core.csumon_bool.restype = \
            ctypes.c_int

        self.core.csumon_array_element.argtypes = \
            [ctypes.c_char_p, ctypes.c_int]
        self.core.csumon_array_element.restype = \
            ctypes.c_double

        self.core.csumon_SV.argtypes = \
            [ctypes.c_char_p]
        self.core.csumon_SV.restype = \
            ctypes.c_double

        self.core.csumon_state_variables.argtypes = \
            [ctypes.c_char]
        # Note c_void_p instead of c_char_p.
        self.core.csumon_state_variables.restype = \
            ctypes.c_void_p

        self.core.csumon_derivatives.argtypes = \
            [ctypes.c_char]
        # Note c_void_p instead of c_char_p.
        self.core.csumon_derivatives.restype = \
            ctypes.c_void_p

        self.core.csumon_variable_info_role.argtypes = \
            [ctypes.c_char_p]
        # Note c_void_p instead of c_char_p.
        self.core.csumon_variable_info_role.restype = \
            ctypes.c_void_p

        self.core.csumo_variable_info_unit.argtypes = \
            [ctypes.c_char_p]
        # Note c_void_p instead of c_char_p.
        self.core.csumo_variable_info_unit.restype = \
            ctypes.c_void_p

        self.core.csumon_time_days.restype = \
            ctypes.c_double

        self.core.csumon_time_ms.restype = \
            ctypes.c_longlong

        self.core.csumon_send_command.argtypes = \
            [ctypes.c_char_p]

        self.core.csumon_all_messages.argtypes = \
            [ctypes.c_char]
        self.core.csumon_all_messages.restype = \
            ctypes.c_char_p

        self.core.csumon_use_license.argtypes = \
            [ctypes.c_char_p]
        self.core.csumon_use_license.restype = \
            ctypes.c_short

        # Note c_void_p instead of c_char_p.
        self.core.csumon_machine_identification_code.restype = \
            ctypes.c_void_p

        self.core.csumon_free.argtypes = \
            [ctypes.c_void_p]


    # csumon_create() is used only internally, no need to make visible.


    def destroy(self):
        self.core.csumon_destroy()


    def force_quit(self):
        self.core.csumon_force_quit()


    def load_model(self, project_name):
        def _internal_datacomm_callback(handle):
            if self.datacomm_callback is not None:
                return self.datacomm_callback(self)
            else:
                return 0


        def _internal_message_callback(handle):
            msg_stream = self.all_messages()

            if msg_stream is not None:
                for msg in msg_stream.split(';'):
                    if '530036' in msg: self.script_loaded = True
                    # MESSAGE_CORE_LOOP_STARTED indicates model is ready.
                    if '530049' in msg: self.model_initialized = True
                    # Redundant, we have a callback for this.
                    if '530004' in msg: self.simulation_finished = True
                    self.messages.append(msg)
            if self.message_callback is not None:
                return self.message_callback(self)
            else:
                return 0


        def _internal_simulation_finished_callback(handle):
            self.simulation_finished = True
            if self.simulation_finished_callback is not None:
                return self.simulation_finished_callback(self)
            else:
                return 0


        if self.model_loaded:
            print(
                'A model is already loaded. Unload it before loading the next one.'
            )
            return -1

        model_name = ''
        if project_name.endswith(".sumo"):
            self.tempdir = tempfile.mkdtemp()
            project = zipfile.ZipFile(project_name, 'r')
            project.extractall(self.tempdir)
            project.close()
            model_name = os.path.join(
                self.tempdir, 'sumoproject.dll'
            ).encode('utf8')
        else:
            model_name = project_name.encode('utf8')

        print("Trying to load model:", model_name)
        # We rely here on the new C API load model which starts the core as well.
        load_result = self.core.csumon_load_model(model_name)
        if load_result != 0:
            print('Error during model load...')
            return load_result

        CALLBACKFUNC = \
            ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)

        # The internal callbacks will manage the user callbacks.
        self.c_datacomm_callback = \
            CALLBACKFUNC(_internal_datacomm_callback)
        self.c_message_callback = \
            CALLBACKFUNC(_internal_message_callback)
        self.c_simulation_finished_callback = \
            CALLBACKFUNC(_internal_simulation_finished_callback)

        self.core.csumon_register_datacomm_cb(
            self.c_datacomm_callback
        )
        self.core.csumon_register_message_cb(
            self.c_message_callback
        )
        self.core.csumon_register_simulation_finished_cb(
            self.c_simulation_finished_callback
        )

        self.model_loaded = True
        return load_result


    def unload_model(self):
        if not self.model_loaded:
            print('No model is loaded')
            return
        self.core.csumon_unload_model()
        if self.platform_name == 'Windows':
            time.sleep(1)
            shutil.rmtree(self.tempdir)
        self.model_loaded = False


    # csumon_start_core_session() is only used internally

    # csumon_register_datacomm_cb() is only used internally

    # csumon_register_simulation_finished_cb() is only used internally

    # csumon_register_message_cb() is only used internally


    def set_mode(self, mode):
        self.core.csumon_set_mode(mode)


    def real_var(self, symbol):
        return self.core.csumon_real(symbol)


    def int_var(self, symbol):
        return self.core.csumon_int(symbol)


    def bool_var(self, symbol):
        isTrue = self.core.csumon_bool(symbol)
        if isTrue:
            return True
        else:
            return False


    def string_var(self, symbol):
        ptr = self.core.csumon_string(symbol)
        str = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf8')
        self.core.csumon_free(ptr)
        return str


    def array_size(self, symbol):
        return self.core.csumon_array_size(symbol)


    def array_element(self, symbol, elemPos):
        return self.core.csumon_array_element(symbol, elemPos)


    def SV(self, symbol): # This function might have a bug. 
        return self.core.csumon_SV(symbol)


    def state_variables(self):
        ptr = self.core.csumon_state_variables(b';')
        str = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf8')
        self.core.csumon_free(ptr)
        return str


    def derivatives(self):
        ptr = self.core.csumon_derivatives(b';')
        str = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf8')
        self.core.csumon_free(ptr)
        return str


    def variable_info_role(self, symbol):
        ptr = self.core.csumon_variable_info_role(symbol)
        str = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf8')
        self.core.csumon_free(ptr)
        return str


    def variable_info_unit(self, symbol):
        ptr = self.core.csumo_variable_info_unit(symbol)
        str = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf8')
        self.core.csumon_free(ptr)
        return str


    def time_days(self):
        return self.core.csumon_time_days()


    def time_ms(self):
        return self.core.csumon_time_ms()


    def send_command(self, command):
        self.core.csumon_send_command(command.encode('utf8'))


    def all_messages(self):
        return self.core.csumon_all_messages(b';').decode('utf8')


    # csumon_use_license is used only internally

    def machine_identification_code(self):
        ptr = self.core.csumon_machine_identification_code()
        str = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf8')
        self.core.csumon_free(ptr)
        return str


    # csumon_free() is used only internally


    # Other utilities.


    def run_model(self):
        if not self.model_loaded:
            print('No model loaded')
            return
        self.simulation_finished = False
        self.send_command("start;")


    def set_stopTime(self, stopTime):
        if not self.model_loaded:
            print('No model loaded')
            return
        stopTimeCommand = 'set Sumo__StopTime ' + str(stopTime) + ';'
        self.send_command(stopTimeCommand)


    def set_dataComm(self, dataComm):
        if not self.model_loaded:
            print('No model loaded')
            return
        dataCommCommand = 'set Sumo__DataComm ' + str(dataComm) + ';'
        self.send_command(dataCommCommand)


    # These just set a member field of the Sumo object, the real registration
    # is in load_model.
    def add_datacomm_callback(self, cb):
        self.datacomm_callback = cb


    def add_message_callback(self, cb):
        self.message_callback = cb


    def add_simulation_finished_callback(self, cb):
        self.simulation_finished_callback = cb
        
