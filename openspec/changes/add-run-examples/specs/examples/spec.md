## ADDED Requirements

### Requirement: R1: Provide runnable batch example
The repository MUST include a Windows batch script under `scripts/` that runs a representative true-scaling OCR comparison end-to-end and writes outputs to `output/plots`, `output/reports`, and `output/data`.
#### Scenario: Run example batch
Given a properly configured `config.ini`
When the user runs `scripts\run_example.bat`
Then the script executes `python src/ocr_true_scaling.py ...` and produces plot/report/CSV files in the output directories

### Requirement: R2: Provide tutorial notebook
The repository MUST include a Jupyter notebook under `notebooks/` showing how to load inputs, construct True(x,z), compute γ/RMSE, and visualize results.
#### Scenario: Open tutorial notebook
Given the user opens `notebooks/ocr_true_scaling_demo.ipynb`
When they run the cells
Then figures are displayed and γ/RMSE values are computed as described

