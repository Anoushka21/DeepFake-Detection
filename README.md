# DeepFake Detection in Face Images

**Objective:**
Use Convolutional Neural Networks to detect deepfakes in Face Images
![Data](dataset.png)

## Create Virtual Environment 
The following commands can be used to create the conda environment and install all necessary dependencies:
```bash
python -m venv df_venv
pip install -r requirements.txt
```
## Dataset
[here](https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces/data).
To install data on HPC, first generate the API token, then run the following command.
```bash
kaggle datasets download -d xhlulu/140k-real-and-fake-faces
``` 

## Executing Experiments
Change path to data in the code
```bash
sbatch slurm_script.batch
```

## Notes
Done as part of the Computer Vision course by Prof. Rob Fergus @NYU Courant Fall 23
