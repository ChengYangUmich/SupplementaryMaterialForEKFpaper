# An Adaptive Real-time Grey-box Model for Advanced Control and Operations in WRRFs

**Cheng Yang <sup>a</sup>, Peter Seiler <sup>b</sup>, Evangelia Belia <sup>c</sup>, Glen T. Daigger <sup>a,*</sup>**

<sup>a</sup> Civil and Environmental Engineering, University of Michigan, 2350 Hayward St, G.G. Brown Building, Ann Arbor, MI 48109, US  
<sup>b</sup> Electrical Engineering and Computer Science, University of Michigan, 1301 Beal Avenue, EECS Building, Ann Arbor, MI 48109, US  
<sup>c</sup> Primodal Inc., 145 Rue Aberdeen, Quebec City, Quebec, CA

<img align="center" src="Graphical Abstract.png" width="800">

**ABSTRACT**
Grey-box models, which combine the explanatory power of first-principle models with the ability to detect subtle patterns from data, are
gaining increasing attention in wastewater sectors. Intuitive, simple structured but fit-for-purpose grey-box models that capture time-varying
dynamics by adaptively estimating parameters are desired for process optimization and control. As an example, this study presents the
identification of such a grey-box model structure and its further use by an Extended Kalman Filter (EKF), for the estimation of the nitrification
capacity and ammonia concentrations of a typical Modified Ludzack-Ettinger (MLE) process. The EKF was implemented and evaluated in real
time by interfacing Python with SUMO (Dynamita™), a widely used commercial process simulator. The EKF was able to accurately estimate
the ammonia concentrations in multiple tanks when given only the concentration in one of them. Besides, the nitrification capacity of the
system could be tracked in real time by the EKF, which provides intuitive information for facility managers and operators to monitor and
operate the system. Finally, the realization of EKF is critical to the development of future advance control, for instance, model predictive
control. Q3

**Key words**: activated sludge, extended Kalman filter, grey-box model, parameter estimation, SUMO

**Publication DOI:** doi: 10.2166/wst.2021.408

**HIGHLIGHTS**
• The development of an adaptive real-time grey-box model with intuitive information is presented.
• The need of model adaptivity was identified and fulfilled by the Extended Kalman Filter.
• The extracted real-time intuitive information will help WRRFs staff in operations and management.
• Model structure simplicity and development pathway encourages applications for other processes.
