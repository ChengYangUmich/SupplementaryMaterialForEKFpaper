function [dx, y] = MLE3Tanks_1r(t,x,u,r1,V,KNH,KOA1,KOA2,KOA3,fr,varargin)
% Output equations 
% x(1) SNH1; x(2) SNH2; X(3) SNH3
y = eye(length(x))*x;

% notation for u
% Disturbance u
% u(1) - QPE
% u(2) - QRAS
% u(3) - QMLE
% u(4) - TKN
% u(5) - MLSS  - no use

% Colltrable u 
% u(6) - SO1 
% u(7) - SO2
% u(8) - SO3
Qtot = u(1) +u(2)+ u(3);
D = 1/V*[-Qtot  0      u(2)+u(3);...
         Qtot  -Qtot   0; ...
         0      Qtot  -Qtot];

% State equations
dx = D*x + [fr*u(1)/V; 0; 0]*u(4) + [r1*u(6)/(u(6)+KOA1);...
    r1*x(2)/(x(2)+KNH)*u(7)/(u(7)+KOA2);...
    r1*x(3)/(x(3)+KNH)*u(8)/(u(8)+KOA3)];

end
