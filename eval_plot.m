function eval_vec = eval_plot(nlgr,ze1,zv1,figure_name)
eval_vec = nan(1,12); 

ye1 = compare(nlgr,ze1);
yv1 = compare(nlgr,zv1);

Fig1 = figure('Position',[50,50,800,600]);
[ha, pos]=tight_subplot(3,2,[0 0],[.08 .05],[.05 .05]);

y1_min = floor(min([ze1.y(:,1);zv1.y(:,1);ye1.y(:,1); yv1.y(:,1);]));
y2_min = floor(min([ze1.y(:,2);zv1.y(:,2);ye1.y(:,2); yv1.y(:,2);]));
y3_min = floor(min([ze1.y(:,3);zv1.y(:,3);ye1.y(:,3); yv1.y(:,3);]));

y1_max = ceil(max([ze1.y(:,1);zv1.y(:,1);ye1.y(:,1); yv1.y(:,1);]));
y2_max = ceil(max([ze1.y(:,2);zv1.y(:,2);ye1.y(:,2); yv1.y(:,2);]));
y3_max = round(max([ze1.y(:,3);zv1.y(:,3);ye1.y(:,3); yv1.y(:,3);]),1)+0.1;

x1_min = min(ze1.SamplingInstants);
x1_max = max(ze1.SamplingInstants);

x2_min = min(zv1.SamplingInstants);
x2_max = max(zv1.SamplingInstants);

% Fig 1 training - SNH1
plot(ha(1),ze1.SamplingInstants,ze1.OutputData(:,1),'o','linewidth',1.5,'MarkerSize',3,'color',[0.8500 0.3250 0.0980]);
hold(ha(1),'on');
plot(ha(1),ye1.SamplingInstants,ye1.OutputData(:,1),'linewidth',1.5,'color',[0 0.4470 0.7410]);
xlim(ha(1),[x1_min x1_max]);
ylim(ha(1),[y1_min y1_max]);
grid(ha(1));
RMSE = sqrt(mean((ze1.OutputData(:,1) -ye1.OutputData(:,1)).^2));
NRMSE = RMSE/range(ze1.OutputData(:,1));
R2 = corrcoef(ze1.OutputData(:,1),ye1.OutputData(:,1));
R2 = R2(1,2);
eval_vec(1,1) = R2;
eval_vec(1,2) = NRMSE;
% text(ha(1),(x1_min+x1_max)/2.5,0.95*y1_max,{['NRMSE = ', num2str(round(NRMSE,2))]; ['R^2 = ', num2str(round(R2,3))]},'fontsize',8);
% text(ha(1),(x1_min+x1_max)/2.5,0.95*y1_max,{'Training'},'fontsize',20);
xlabel(ha(1),'');
xticklabels(ha(1),'');
ylabel(ha(1),'SNH1 ,mg/L');
hold(ha(1),'off');
% legend(ha(1),'SUMO','Grey box');
title(ha(1),'Training','fontsize',18);
% Fig 2 - Testing -SNH1
plot(ha(2),zv1.SamplingInstants,zv1.OutputData(:,1),'o','linewidth',1.5,'MarkerSize',3,'color',[0.8500 0.3250 0.0980]);
hold(ha(2),'on');
plot(ha(2),yv1.SamplingInstants,yv1.OutputData(:,1),'linewidth',1.5,'color',[0 0.4470 0.7410]);
xlim(ha(2),[x2_min x2_max]);
ylim(ha(2),[y1_min y1_max]);
grid(ha(2));
RMSE = sqrt(mean((zv1.OutputData(:,1) -yv1.OutputData(:,1)).^2));
NRMSE = RMSE/range(zv1.OutputData(:,1));

R2 = corrcoef(zv1.OutputData(:,1),yv1.OutputData(:,1));
R2 = R2(1,2);
eval_vec(1,3) = R2;
eval_vec(1,4) = NRMSE;
% text(ha(2),(x2_min+x2_max)/2.5,0.95*y1_max,{['NRMSE = ', num2str(round(NRMSE,2))]; ['R^2 = ', num2str(round(R2,3))]},'fontsize',8);
% text(ha(2),(x2_min+x2_max)/2,0.95*y1_max,{'Testing'},'fontsize',20);
xlabel(ha(2),'');
xticklabels(ha(2),'');
ylabel(ha(2),'');
yticklabels(ha(2),'');
hold(ha(2),'off');
legend(ha(2),'SUMO','Grey box');
title(ha(2),'Testing','FontSize',18);
% Fig 3 Training - SNH2
plot(ha(3),ze1.SamplingInstants,ze1.OutputData(:,2),'o','linewidth',1.5,'MarkerSize',3,'color',[0.8500 0.3250 0.0980]);
hold(ha(3),'on');
plot(ha(3),ye1.SamplingInstants,ye1.OutputData(:,2),'linewidth',1.5,'color',[0 0.4470 0.7410]);
xlim(ha(3),[x1_min x1_max]);
ylim(ha(3),[y2_min y2_max]);
grid(ha(3));
RMSE = sqrt(mean((ze1.OutputData(:,2) -ye1.OutputData(:,2)).^2));
NRMSE = RMSE/range(ze1.OutputData(:,2));
R2 = corrcoef(ze1.OutputData(:,2),ye1.OutputData(:,2));
R2 = R2(1,2);
eval_vec(1,5) = R2;
eval_vec(1,6) = NRMSE;
% text(ha(3),(x1_min+x1_max)/2.5,0.9*y2_max,{['NRMSE = ', num2str(round(NRMSE,2))]; ['R^2 = ', num2str(round(R2,3))]},'fontsize',8);

xlabel(ha(3),'');
xticklabels(ha(3),'');
ylabel(ha(3),'SNH2 ,mg/L');
hold(ha(3),'off');
% legend(ha(3),'True','Indentified');

% Fig 4 - Testing - SNH2
plot(ha(4),zv1.SamplingInstants,zv1.OutputData(:,2),'o','linewidth',1.5,'MarkerSize',3,'color',[0.8500 0.3250 0.0980]);
hold(ha(4),'on');
plot(ha(4),yv1.SamplingInstants,yv1.OutputData(:,2),'linewidth',1.5,'color',[0 0.4470 0.7410]);
xlim(ha(4),[x2_min x2_max]);
ylim(ha(4),[y2_min y2_max]);
grid(ha(4));
RMSE = sqrt(mean((zv1.OutputData(:,2) -yv1.OutputData(:,2)).^2));
NRMSE = RMSE/range(zv1.OutputData(:,2));
R2 = corrcoef(zv1.OutputData(:,2),yv1.OutputData(:,2));
R2 = R2(1,2);
eval_vec(1,7) = R2;
eval_vec(1,8) = NRMSE;
% text(ha(4),(x2_min+x2_max)/2.5,0.9*y2_max,{['NRMSE = ', num2str(round(NRMSE,2))]; ['R^2 = ', num2str(round(R2,3))]},'fontsize',8);

xlabel(ha(4),'');
xticklabels(ha(4),'');
ylabel(ha(4),'');
yticklabels(ha(4),'');
hold(ha(4),'off');
% legend(ha(4),'True','Indentified');

% Fig 5 - SNH3 - training 
plot(ha(5),ze1.SamplingInstants,ze1.OutputData(:,3),'o','linewidth',1.5,'MarkerSize',3,'color',[0.8500 0.3250 0.0980]);
hold(ha(5),'on');
plot(ha(5),ye1.SamplingInstants,ye1.OutputData(:,3),'linewidth',1.5,'color',[0 0.4470 0.7410]);
xlim(ha(5),[x1_min x1_max]);
ylim(ha(5),[y3_min y3_max]);
grid(ha(5));
RMSE = sqrt(mean((ze1.OutputData(:,3) -ye1.OutputData(:,3)).^2));
NRMSE = RMSE/range(ze1.OutputData(:,3));
R2 = corrcoef(ze1.OutputData(:,3),ye1.OutputData(:,3));
R2 = R2(1,2);
eval_vec(1,9) = R2;
eval_vec(1,10) = NRMSE;
% text(ha(5),(x1_min+x1_max)/2.5,0.9*y3_max,{['NRMSE = ', num2str(round(NRMSE,2))]; ['R^2 = ', num2str(round(R2,3))]},'fontsize',8);

xlabel(ha(5),'Time ,days');
ylabel(ha(5),'SNH3 ,mg/L');
hold(ha(5),'off');
% legend(ha(5),'True','Indentified');

% Fig 6 -SNH3- testing 
plot(ha(6),zv1.SamplingInstants,zv1.OutputData(:,3),'o','linewidth',1.5,'MarkerSize',3,'color',[0.8500 0.3250 0.0980]);
hold(ha(6),'on');
plot(ha(6),yv1.SamplingInstants,yv1.OutputData(:,3),'linewidth',1.5,'color',[0 0.4470 0.7410]);
xlim(ha(6),[x2_min x2_max]);
ylim(ha(6),[y3_min y3_max]);
grid(ha(6));
RMSE = sqrt(mean((zv1.OutputData(:,3) -yv1.OutputData(:,3)).^2));
NRMSE = RMSE/mean(zv1.OutputData(:,3));
R2 = corrcoef(zv1.OutputData(:,3),yv1.OutputData(:,3));
R2 = R2(1,2);
eval_vec(1,11) = R2;
eval_vec(1,12) = NRMSE;
% text(ha(6),(x2_min+x2_max)/2.5,0.9*y3_max,{['NRMSE = ', num2str(round(NRMSE,2))]; ['R^2 = ', num2str(round(R2,3))]},'fontsize',8);

xlabel(ha(6),'Time ,days');
ylabel(ha(6),'');
yticklabels(ha(6),'');
hold(ha(6),'off');
% legend(ha(6),'True','Indentified');

%%
saveas(Fig1,figure_name); 
end

