# Occupancy Dataset Generator

This is a pipeline to generate occupancy datasets.  


### Dependencies

Please find dependencies in [requirements.txt]()

### Installing

See [setup.md](https://github.com/shubham-monarch/pixel-perfect-sfm/blob/rig_ba/setup.md) for installtion steps

### Executing program

Put the files / folders to be processed inside the `input` folder. The ouput would be generated in the `output` folder with
the same relative structure as that of `input`. 

e.g. input folder 

└── RJM                                                                                                           
    └── 2024_06_06_utc                                                                           
        └── front              
            ├── front_2024-06-05-08-54-33svo                                                                     
            ├── front_2024-06-05-09-09-54.svo                                                                       
            ├── front_2024-06-05-09-14-54.svo                                                                      
            ├── front_2024-06-05-09-19-54.svo     

The corresponding `output` folder would also have the same structure => 

└── RJM                                                                                                           
    └── 2024_06_06_utc                                                                           
        └── front              
            ├── front_2024-06-05-08-54-33svo                                                                     
            ├── front_2024-06-05-09-09-54.svo                                                                       
            ├── front_2024-06-05-09-14-54.svo                                                                      
            ├── front_2024-06-05-09-19-54.svo     


### Logging
check out the `logs` folder

