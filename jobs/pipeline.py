from azureml.core import Workspace, Dataset, ComputeTarget, Environment, Experiment
from azureml.core.compute import AmlCompute
from azureml.core.compute_target import ComputeTargetException


ws = Workspace.from_config('.azureml/')
input_ds = Dataset.get_by_name(workspace=ws, name ='penguine_iter')

# ---------------------------------------------------------------------------------------------
# Creating Compute target
# ---------------------------------------------------------------------------------------------
compute_name = 'AML-compute-02'
try:
    compute_target = ws.compute_targets[compute_name]
    print(f'compute : {compute_name} is available acessing it .....')

except ComputeTargetException as e:
    print(f'compute : {compute_name} is not available, creating new....')
    provisioning_configuration = AmlCompute.provisioning_configuration(vm_size = 'Standard_DS11_v2',max_nodes = 1)
    compute_target = ComputeTarget.create(workspace=ws,
                                          name=compute_name,
                                          provisioning_configuration=provisioning_configuration)


# ---------------------------------------------------------------------------------------------
# Creating Custom environment
# ---------------------------------------------------------------------------------------------
my_env_name = 'penguine_env'

if my_env_name in ws.environments:
    my_env = ws.environments[my_env_name]
    print(f"Environment '{my_env_name}' already exists, fetched it.")
else:   
    print(f"Environment '{my_env_name}' doesn't exist, creating it.")

    from azureml.core.conda_dependencies import CondaDependencies

    my_env = Environment('penguine_env')
    conda_dep = CondaDependencies()
    requirements_file = 'requirements.txt'

    with open(requirements_file,"r") as file:
        for line in file:
            package_name = line.strip()
            if package_name:
                if "azureml" in package_name:
                    conda_dep.add_pip_package(package_name)
                else:
                    conda_dep.add_conda_package(package_name)

    my_env.python.conda_dependencies = conda_dep
    my_env.register(workspace=ws)



from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep
