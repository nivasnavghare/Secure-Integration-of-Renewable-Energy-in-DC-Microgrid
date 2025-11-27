%% Simulink Simulation Executor
% Simple test runner for DC Microgrid models

clear all; close all; clc;

fprintf('\n════════════════════════════════════════════════════════════\n');
fprintf('DC MICROGRID SIMULINK SIMULATION EXECUTION\n');
fprintf('════════════════════════════════════════════════════════════\n\n');

% Load parameters
model_parameters;

% Clean up old models
bdclose('all');

fprintf('\n[STEP 1] Creating Simulink Models\n');
fprintf('─────────────────────────────────────────────────────────────\n\n');

try
    % Create model 1
    fprintf('Creating DC_Microgrid_Complete model...\n');
    new_system('DCMic_Complete', 'Model');
    open_system('DCMic_Complete');
    set_param('DCMic_Complete', 'SolverType', 'Fixed-step');
    set_param('DCMic_Complete', 'Solver', 'ode4');
    set_param('DCMic_Complete', 'FixedStep', '1');
    set_param('DCMic_Complete', 'StopTime', '100');  % 100 seconds for testing
    
    % Add simple blocks
    add_block('simulink/Sources/Sine Wave', 'DCMic_Complete/PV', ...
        'Amplitude', '25000', 'Bias', '25000', 'Frequency', '0.01');
    add_block('simulink/Sources/Sine Wave', 'DCMic_Complete/Wind', ...
        'Amplitude', '10000', 'Bias', '15000', 'Frequency', '0.05');
    add_block('simulink/Math Operations/Sum', 'DCMic_Complete/Total');
    add_block('simulink/Sinks/Scope', 'DCMic_Complete/Output');
    
    % Connect
    add_line('DCMic_Complete', 'PV/1', 'Total/1');
    add_line('DCMic_Complete', 'Wind/1', 'Total/2');
    add_line('DCMic_Complete', 'Total/1', 'Output/1');
    
    save_system('DCMic_Complete');
    fprintf('  ✓ Model 1 created\n\n');
    
    % Run simulation
    fprintf('[STEP 2] Executing Simulations\n');
    fprintf('─────────────────────────────────────────────────────────────\n\n');
    
    fprintf('Running DC_Microgrid_Complete (100 second test)...\n');
    tic;
    out1 = sim('DCMic_Complete');
    t1 = toc;
    fprintf('  ✓ Completed in %.2f seconds\n\n', t1);
    
    % Display results
    fprintf('[RESULTS]\n');
    fprintf('─────────────────────────────────────────────────────────────\n\n');
    fprintf('✅ Simulation 1: DC_Microgrid_Complete\n');
    fprintf('   Status: SUCCESS\n');
    fprintf('   Duration: 100 seconds\n');
    fprintf('   Time Step: 1 second\n');
    fprintf('   Data Points: 100\n');
    fprintf('   Execution Time: %.3f seconds\n\n', t1);
    
    fprintf('════════════════════════════════════════════════════════════\n');
    fprintf('SUMMARY\n');
    fprintf('════════════════════════════════════════════════════════════\n\n');
    fprintf('Total Simulations: 1\n');
    fprintf('Successful: 1 ✅\n');
    fprintf('Failed: 0\n');
    fprintf('Total Execution Time: %.2f seconds\n\n', t1);
    fprintf('🎉 SIMULATION EXECUTION SUCCESSFUL!\n');
    fprintf('════════════════════════════════════════════════════════════\n\n');
    
    % Save results
    save('sim_results.mat', 'out1');
    fprintf('Results saved to: sim_results.mat\n\n');
    
catch ME
    fprintf('\n❌ ERROR: %s\n', ME.message);
    fprintf('Location: %s (line %d)\n', ME.stack(1).file, ME.stack(1).line);
end

bdclose('all');
