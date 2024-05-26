

import os


class SPMFConverter:

    def convert_floats_to_number_items(self, file_path, input_file):
        """
        Converts the input file with fload values into a format compatible with SPMF.
        first it open the file and read the lines, 
        then it iterates over the lines of the file and convert each float value to number.
        then creates a output file name by replacing the .txt with _converted.txt
        then writes the converted file
        close the converted file
        return the output file name
        Args:
            file_paht (str): The path to the input text file.     
            input_file (str): The name of the input text file.  
        returns:
            output_file_name (str): The name of the output text file.
        """        
        # Open the input file and read the lines
        # Read the input file
        input_file_full_name = os.path.join(file_path, input_file)        
        with open(input_file_full_name, 'r') as file:
            lines = file.readlines()

        # Convert each float value to number
        converted_lines = [str(int(float(line.strip().replace('.', '')))) for line in lines]

        # Create the output file name
        #output_file_name = input_file.replace('.txt', '_converted.txt')
        output_file_name = input_file
        output_file_full_name = os.path.join(file_path, output_file_name)         
        
        output_file_full_name = os.path.join(file_path, output_file_name)        
        # Write the converted file
        with open(output_file_full_name, 'w') as file:         
            file.write('\n'.join(converted_lines))

        # Close the converted file
        file.close()

        # Return the output file name
        return output_file_name  
        
    def convert_nulls_to_number_items(self, file_path, input_file):
            """
            Converts the input file with null values into a format compatible with SPMF.
            first it open the file and read the lines, 
            then it iterates over the lines of the file and convert each float value to number.
            then creates a output file name by replacing the .txt with _converted.txt
            then writes the converted file
            close the converted file
            return the output file name
            Args:
                file_paht (str): The path to the input text file.     
                input_file (str): The name of the input text file.  
            returns:
                output_file_name (str): The name of the output text file.
            """        
            # Open the input file and read the lines
            # Read the input file
            input_file_full_name = os.path.join(file_path, input_file)     
            # Open the input file to read and update
            with open(input_file_full_name, 'r+') as file:
                # Read each line of the file
                lines = file.readlines()
                # Iterate over the lines and replace 'null' or '' with 0
                for i in range(len(lines)):
                    if lines[i].strip() == 'null' or lines[i].strip() == '':
                        lines[i] = '0\n'
                # Move the file pointer to the beginning of the file
                file.seek(0)
                # Write the modified lines back to the file
                file.writelines(lines)
                # Truncate the remaining content in the file
                file.truncate()
            # Close the file
            file.close()
            
            # Return the output file name
            return input_file          
        
    def convert_text_to_identified_items(self, file_path, input_file):
        """
        Converts the input text file into a format compatible with SPMF.
        Args:
            input_file (str): The path to the input text file.
        Returns:
            None
        """

        # Read the input file
        input_file_full_name = os.path.join(file_path, input_file)
        with open(input_file_full_name, 'r') as file:
            lines = file.readlines()
            file.close()

        # Create a dictionary to store the mapping of texts to ids
        text_to_id = {}
        id_counter = 1

        # Iterate over the lines of the file
        for line in lines:
            text = line.strip()
            # Check if the text is distinct
            if text not in text_to_id:
                #check if text is not null
                if text == 'null':
                    text = 0
                # Assign a new id to the text
                text_to_id[text] = id_counter
                id_counter += 1

        # Create the output file name
        #output_file_name = input_file.replace('.txt', '_converted.txt')
        output_file_name = input_file
        output_file_full_name = os.path.join(file_path, output_file_name)        

        # Write the converted file
        with open(output_file_full_name, 'w') as file:        
            # Write the conversion information
            file.write('@CONVERTED_FROM_TEXT\n')
            for text, id in text_to_id.items():
                file.write(f'@ITEM={id}={text}\n')

            # Write the converted items
            for line in lines:
                text = line.strip()
                id = text_to_id[text]
                file.write(f'{id}\n')

            # Close the file
            file.close()
        return output_file_name

# Example usage
#converter = SPMFConverter()
#converter.convert_text_to_identified_items('/c:/gitHub/utad/utad-ea-mining/app/src/api_gateway_load/utils/input.txt')



