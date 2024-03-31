from spmf import Spmf

# spmf = Spmf("PrefixSpan", input_file_path="./contextPrefixSpan.txt",
#             output_file_path="output.txt", 
#             spmf_jar_location_dir="./spmf.jar")

#smpfa = Spmf(spmf_bin_location_dir="c:/gitHub/utad/utad-ea-mining/app/src/studies/spmf/spmf.jar",
smpfa = Spmf(spmf_bin_location_dir="c:/gitHub/utad/utad-ea-mining/app/src/studies/spmf",
              algorithm_name="PrefixSpan", 
              input_filename="c:/gitHub/utad/utad-ea-mining/app/src/studies/spmf/contextPrefixSpan.txt",
              output_filename="c:/gitHub/utad/utad-ea-mining/app/src/studies/spmf/output.txt")

smpfa.run()
print(smpfa.to_pandas_dataframe(pickle=True))
smpfa.to_csv("output.csv")