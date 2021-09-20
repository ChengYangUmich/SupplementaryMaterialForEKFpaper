function [] = display_input(z,figure_name)
time = z.samplingInstance;

figure('Position',[50,50,600,600]);
subplot(3,2,1);
plot(time, z.u(:,1),'linewidth',1.5);
xlim([0 7]);
ylim([12000 36000]);
grid on;
box on;
ylabel('QPE, m3/d');
xlabel('Time, day');
title('QPE');

subplot(3,2,3);
plot(time, z.u(:,4),'linewidth',1.5);
xlim([0 7]);
ylim([30 90]);
grid on;
box on;
ylabel('TKN, mg/L');
xlabel('Time, day');
title('TKN');

subplot(3,2,2);
plot(time, z.u(:,6),'linewidth',1.5);
xlim([0 7]);
ylim([0 3.2]);
grid on;
box on;
ylabel('SO1, mg/L');
xlabel('Time, day');
title('SO1');
subplot(3,2,4);
plot(time, z.u(:,7),'linewidth',1.5);
xlim([0 7]);
ylim([0 3.2]);
grid on;
box on;
ylabel('SO2, mg/L');
xlabel('Time, day');
title('SO2');
subplot(3,2,6);
plot(time, z.u(:,8),'linewidth',1.5);
xlim([0 7]);
ylim([0 3.2]);
grid on;
box on;
ylabel('SO3, mg/L');
xlabel('Time, day');
title('SO3');
saveas(gcf,figure_name); 
end

