from azureml.train.automl import AutoMLConfig
from azureml.core import Dataset, Workspace
from azureml.core import ComputeTarget
from azureml.core.compute import AmlCompute

#------------------------------------------------------------------------------------------
# Retrieving Workspace and loading dataset
#-------------------------------------------------------------------------------------------
ws = Workspace.from_config('.azureml/')
input_ds = Dataset.get_by_name(workspace=ws, name ='penguine_iter')

#------------------------------------------------------------------------------------------
# Creating Compute targets
#-------------------------------------------------------------------------------------------
compute_machine_name = 'AML-compute-02'

if compute_machine_name in ws.compute_targets:
    compute_machine = ws.compute_targets[compute_machine_name]
else:
    provisioning_configuration = AmlCompute.provisioning_configuration(vm_size = 'Standard_DS11_v2',max_nodes = 1)
    compute_machine = ComputeTarget.create(workspace=ws,
                                           name=compute_machine_name,
                                           provisioning_configuration=provisioning_configuration,)
    
    compute_machine.wait_for_completion(show_output=True)

#------------------------------------------------------------------------------------------
# Creating AutoML config
#-------------------------------------------------------------------------------------------
automl_config = AutoMLConfig(task = 'classification',
                            compute_target = compute_machine,
                            training_data = input_ds,
                            label_column_name = 'Species',
                            n_cross_validation = 3,
                            primary_metric = 'norm_macro_recall',
                            iteration = 3,
                            max_concurrent_iteration = 1,
                            experiment_timeout_hour = 0.25,
                            featurization = 'auto'
                            )

#------------------------------------------------------------------------------------------
# Creating Experiment and submitting run
#-------------------------------------------------------------------------------------------
from azureml.core import Experiment

automl_experiment = Experiment(workspace=ws,name= 'Penguine_automl_sdk_03')
automl_run = automl_experiment.submit(automl_config)

automl_run.wait_for_completion(show_output=True)

#------------------------------------------------------------------------------------------
# Retrieving best models
#-------------------------------------------------------------------------------------------

results = []

for child_run in automl_run.get_children():
    run_id = child_run.id
    model_name = model_name = child_run.properties.get('run_algorithm', 'Unknown')
    score = child_run.get_metrics().get('norm_macro_recall')
    

    if score:
        results.append({
            'Algorithm' : model_name,
            'Metric Name': 'Norm_Macro_Recall',
            'Score': score
        })


import pandas as pd
AutoML_result_df = pd.DataFrame(results)
AutoML_result_df = AutoML_result_df.loc[AutoML_result_df.groupby('Algorithm')['Score'].idxmax()]
AutoML_result_df = AutoML_result_df.sort_values(by = 'Score', ascending = False)

print(AutoML_result_df)

import os 
output_folder = os.path.join(os.getcwd(),"AutoML")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_file_path = os.path.join(output_folder,'AutoML_result_df.csv')

AutoML_result_df.to_csv(output_file_path,index=False)

