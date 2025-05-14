- The data we used are basically `Data/merged_all_data_en.csv` and `Data/bubble_data_full.csv`. The former is used for most visualization charts for pollution analysis, and the latter one is specifically used for the bubble chart. The reason why we used two different data sets is that the former one is more comprehensive and contains more data points, while the latter one is more detailed and contains more information, specifically in terms of data layouts.

- The `Data/merged_all_data_en.csv` file is also being aggregated, processed, cleaned, and translated from raw data. Due to the massive size of the raw data, we cannot upload it here.

- The file `Data/Extras.csv` is the file we used to merge other attributes with the main data set in order to demonstrate rich cross-attribute interconnections.

- The file `dir_tree.txt` shows an original directory tree of the original raw data.

- The `data_preprocesing.ipynb` consists of different cells of Python codes that were used to preprocess the data. For example, reorganize the data, and data cleaning.

- The directories `backend` and `frontend` contain the code for the backend and frontend of the web application. We use Python and Flask for the backend, and Vue with D3 for the frontend.
