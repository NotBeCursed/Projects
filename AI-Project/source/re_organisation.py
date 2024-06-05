import os
import csv
import shutil  

def re_organisation(path_db):
    """This function allow to reorganise test and train directory"""
    
    # Scan DB directory
    with os.scandir(path_db) as entries:
        for entry in entries:
            new_path = path_db+"/"+entry.name # ./dataset + the directory
            #print(new_path)
            
            # If "new_path" is a directory (= train or test)
            if os.path.isdir(new_path):
                # Create the new directory 
                for i in range (10):
                    os.makedirs(new_path+"/"+str(i), exist_ok=True)

                # Read csv file
                file = f'{new_path}_data.csv'
                #print(file)
                with open(file, newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for row in reader:
                        image,labels = row
                        #print(image, labels)
                        #print(os.path.isfile(f'./{image}'))
                        if (os.path.isfile(f'./{image}')):
                            image_name = image.split('/')[2]
                            print(f"{image_name} moved")
                            shutil.move(f'./{image}', f'{new_path}/{labels}/{image_name}')
                            
if __name__ == "__main__":
    re_organisation("./dataset")