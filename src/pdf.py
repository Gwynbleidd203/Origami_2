from dataclasses import dataclass
import os
import pypdf
import time

from progress.bar import Bar
from typing import Literal, List

from utils.bcolors import bcolors
from utils.clear_terminal import clear_terminal

@dataclass
class RetrievedFilesType:
    name: str
    path: str
    created_at: str
    last_modified_at: str

class ResizePDF:

    def __init__(
            self, 
            input_path: str, 
            output_path: str, 
            desired_format: Literal["A2","A3", "A4", "A5", "L13"], 
            order_by: Literal["creation_date", "last_modification_date", "name"]="name",
            use_custom_order: bool=False,
            custom_order_path: str='order.txt'
        ) -> None:

        self.__input_path = input_path
        self.__input_filename = os.path.basename(input_path)
        self.__output_path = f'{output_path}{self.__input_filename}'
        self.__desired_format = desired_format
        self.__desired_doc_type = 'pdf'
        self.__order_by = order_by

        self.__USE_CUSTOM_ORDER = use_custom_order
        self.__CUSTOM_ORDER_PATH = custom_order_path
        self.__MEASEURE_POINTS = 2.83464567

        self.__formats = {
            "A2": (420, 594),
            "A3": (297, 420),
            "A4": (210, 297),
            "A5": (148, 210)
        }

        self.__desired_dimensions = self.mm_to_point_transformation()

        os.makedirs(output_path, exist_ok=True)

        self.__report = []

    def is_pdf(self, file: str) -> bool:
        """Check if a file is a PDF.

        Args:
            file (str): The name of the file.

        Returns:
            bool: True if the file is a PDF, False otherwise.
        """

        filename = file or self.__input_filename

        return filename.split('.')[-1].lower() == self.__desired_doc_type
    

    def retrieve_custom_pdfs(self) -> List[RetrievedFilesType]:

        """Gera uma lista com todos os PDFs do caminho especificado

        Returns:
            list: List of PDF file paths.
        """

        document_list = []

        for doc in self.read_order_from_file():

            created_at, last_modified_at = self.get_doc_info(doc)

            document_list.append(
                {
                    "name": os.path.basename(doc),
                    "path": doc,
                    "created_at": created_at,
                    "last_modified_at": last_modified_at
                }
            )

        return document_list


    def retrieve_pdfs_per_folder(self) -> List[RetrievedFilesType]:
        """Retrieve a list of PDF files in the input folder.

        Returns:
            list: List of PDF file paths.
        """

        document_list = os.listdir(self.__input_path)

        pdf_list = []

        for doc in document_list:

            if self.is_pdf(doc):

                print(doc)

                created_at, last_modified_at = self.get_doc_info(f'{self.__input_path}{doc}')

                pdf_list.append(
                    {
                        "name": doc,
                        "path": f'{self.__input_path}{doc}',
                        "created_at": created_at,
                        "last_modified_at": last_modified_at
                    }
                )

        ordenated_pdf_list = self.ordenate_files(pdf_list)

        self.write_order_in_txt(ordenated_pdf_list)

        return ordenated_pdf_list
    

    def ordenate_files(self, pdf_list: List[RetrievedFilesType]) -> List[RetrievedFilesType]:

        if self.__order_by == "name":

            return sorted(pdf_list, key=lambda x: x["name"])
        
        elif self.__order_by == "creation_date":

            return sorted(pdf_list, key=lambda x: x["created_at"])
        
        elif self.__order_by == "last_modification_date":

            return sorted(pdf_list, key=lambda x: x["last_modified_at"])
        
        else:

            return pdf_list
        

    def write_order_in_txt(self, pdf_list:List[RetrievedFilesType], complete_path: bool = True) -> None:

        with open(self.__CUSTOM_ORDER_PATH, 'w') as file:

            for doc in pdf_list:
        
                document_name = doc["name"]
                
                if complete_path == True:

                    document_name = doc["path"]

                file.write(f'{document_name}\n')
        

    def read_order_from_file(self) -> List[str]:
        """
        Read the order of PDF files from a text file.

        The function reads the content of the file specified by the `__CUSTOM_ORDER_PATH` attribute.
        Each line in the file represents a PDF file, and the order of the lines determines the order in which the files will be processed.

        Parameters:
            self (ResizePDF): The instance of the ResizePDF class.

        Returns:
            List[str]: A list of PDF file paths, ordered as specified in the text file.

        Raises:
            FileNotFoundError: If the file specified by `__CUSTOM_ORDER_PATH` does not exist.
            Exception: If any other error occurs while reading the file.
        """

        order_list = []

        try:
            
            with open(self.__CUSTOM_ORDER_PATH, 'r') as file:

                for count, line in enumerate(file):

                    print(f'{bcolors.OKCYAN}{count} - {line}')

                    order_list.append(line.strip())

        except FileNotFoundError:

            print(f'{bcolors.WARNING}File [{self.__CUSTOM_ORDER_PATH}] not found. Please check for misspelled paths.')

        except Exception as err:

            print(f'{bcolors.FAIL}Error while reading file: {err}')

        print('ORDER LIST', order_list)

        return order_list


    def print_documents(self, pdf_list: List[RetrievedFilesType]) -> None:
        """
        Prints a list of retrieved PDF documents with their respective details.

        Parameters:
            pdf_list (List[RetrievedFilesType]): A list of dictionaries, each representing a PDF file.
            Each dictionary contains the 'name', 'path', 'created_at', and 'last_modified_at' of a PDF file.

        Returns:
            None
        """

        print("List of Retrieved PDF Documents:")
        print("{:<30} {:<50} {:<20} {:<20}".format("Name", "Path", "Created At", "Last Modified At"))
        print("-" * 120)
        for doc in pdf_list:
            print("{:<30} {:<50} {:<20} {:<20}".format(doc["name"], doc["path"], doc["created_at"], doc["last_modified_at"]))


    def get_doc_info(self, path: str) -> str:

        creation_time = os.path.getctime(path)
        lastmodified_time = os.path.getmtime(path)

        creation_time = time.ctime(creation_time)
        lastmodified_time = time.ctime(lastmodified_time)

        return  creation_time, lastmodified_time
    
            
    def mm_to_point_transformation(self) -> tuple[float, float]:
        """
            Converts the dimensions from millimeters to points.

            The conversion factor is 2.83464567 points per millimeter.

            Parameters:
            self (ResizePDF): The instance of the ResizePDF class.

            Returns:
            tuple[float, float]: A tuple containing the converted width and height in points.
        """

        print('Antes', (self.__formats[self.__desired_format][0] * self.__MEASEURE_POINTS, self.__formats[self.__desired_format][1] * self.__MEASEURE_POINTS))

        final_width = round(
            self.__formats[self.__desired_format][0] * self.__MEASEURE_POINTS, 3
        )

        final_height = round(
            self.__formats[self.__desired_format][1] * self.__MEASEURE_POINTS, 3
        )
        
        print('Depois', (final_width, final_height))

        return (final_width, final_height)
    

    def get_scale_factor(self, original_dimension: tuple[float, float]) -> tuple[float, float]:
        """
            Calculate a scale factor for the current page width and height to fit in the desired format.

            Args:

                Original dimensions(width and height) from the current page.

            Returns:

                A tuple with the scale factor for x and y axis.
        """

        scale_factor_w = self.__desired_dimensions[0] / original_dimension[0]
        scale_factor_y = self.__desired_dimensions[1] / original_dimension[1]

        scale_factor = (
            scale_factor_w, 
            scale_factor_y
        )

        #print(scale_factor)

        return scale_factor


    def __handle_resize(
        self,
        pdf_file_path: str,
        output_path: str
    ):
        """Resize a PDF file to the desired format.

        Args:
            pdf_file_path (str): The path to the PDF file.
        """

        try:

            print(f'{bcolors.OKBLUE} Processing [{self.__input_filename}]...')

            with open(pdf_file_path, 'rb') as file:

                reader = pypdf.PdfReader(file)
                writer = pypdf.PdfWriter()

                for page_number in range(len(reader.pages)):

                    page = reader.pages[page_number]

                    original_height = float(page.mediabox.height)
                    original_width = float(page.mediabox.width)

                    original_dimension = (original_width, original_height)

                    """ print('MEDIA', page.mediabox)

                    print('CROP', page.cropbox) """

                    #print('Original dimensions', original_width, original_height)

                    # page.cropbox.scale(5, 5)

                    if original_dimension == self.__desired_dimensions:

                        print(f'{bcolors.OKCYAN} Page {page_number + 1} already matches the desired size, skipping.')
                        
                        writer.add_page(page)

                        continue

                    scale_factor = self.get_scale_factor(original_dimension)

                    page.scale(scale_factor[0], scale_factor[1])

                    page.mediabox.lower_left = (0, 0)
                    page.mediabox.upper_right = self.__desired_dimensions  # A4 size: 210 x 297 mm

                    writer.add_page(page)

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

                print(
                    f'{bcolors.OKGREEN}The PDF file ({self.__input_filename}) has been resized with success!'
                )

        except Exception as error:

            print(f'{bcolors.FAIL}An error occurred: ', error)


    def resize_pipeline(self, pdf_list: List[RetrievedFilesType]) -> None:
        """Resize multiple PDF files in a batch.

        Args:
            pdf_list (list): List of PDF file paths.
        """

        print(f'{bcolors.OKBLUE}Converting {len(pdf_list)} files...')

        progress_bar = Bar(
            f'{bcolors.OKBLUE}Processing {self.__input_filename}...', max=len(pdf_list)
        )

        for doc in pdf_list:

            progress_bar.next()

            print(doc)

            self.__input_filename = doc["name"]

            self.__handle_resize(
                doc["path"], self.__output_path + self.__input_filename
            )

        progress_bar.finish()


    def resize_a_single_file(self) -> None:
        """Resize a single PDF file.

        If the input file is not a PDF or is not supported, print an error message.
        """

        if self.is_pdf(self.__input_filename):

            self.__handle_resize(self.__input_path, self.__output_path)

        else:

            print(
                f'{bcolors.FAIL}The file ({self.__input_filename}) is not a PDF or is not supported.')
            

    def resize_using_custom_order(self) -> None:

        custom_list = self.retrieve_custom_pdfs()

        print(f'{bcolors.HEADER}Checking for files veracity...')

        print('/n' * os.get_terminal_size().lines)

        for item in custom_list:

            self.__input_filename = item["name"]

            self.__handle_resize(
                item["path"],
                self.__output_path + self.__input_filename
            )

        """ for item in custom_list:

            if os.path.isfile(f'{self.__input_path}{item["name"]}'):
                
                cleanead_list.append(item)

            else:

                print(f'{bcolors.WARNING}Is not a file. Check for mispelled path names')

                rejected_files.append(item)

                pass

        self.resize_pipeline(custom_list) """


    def resize(self) -> None:
        """Resize PDF files based on the input path.

        If the input path is a file, resize the single file.
        If the input path is a directory, resize all PDF files in the directory.
        """

        if os.path.isfile(self.__input_path):

            self.resize_a_single_file()  # Resize the single file

        elif os.path.isdir(self.__input_path):

            pdf_list = self.retrieve_pdfs_per_folder()  # Retrieve PDFs from the directory

            if len(pdf_list) == 1:

                # Resize the single PDF file
                self.resize_a_single_file(pdf_list[0])

            elif len(pdf_list) > 1:

                self.resize_pipeline(pdf_list)  # Resize multiple PDF files

            else:

                print(f"{bcolors.WARNING}No PDF files found in the directory.")
        else:

            print(f"{bcolors.WARNING}Invalid input path.")


    def generate_report(self):
        """
        Generate a report of the PDF resizing process.

        The report includes the total number of PDF files processed,
        the time taken to process each file, and the total execution time.

        Returns:
            None
        """
        start_time = time.time()

        # Retrieve the list of PDF files
        pdf_list = self.retrieve_pdfs_per_folder()
        num_pdfs = len(pdf_list)

        print(f"Number of PDF files processed: {num_pdfs}")

        total_time = 0

        # Process each PDF file
        for doc in pdf_list:
            start_file_time = time.time()

            # Set the input filename and resize the PDF
            self.__input_filename = doc["name"]
            self.__handle_resize(doc["path"], self.__output_path + self.__input_filename)

            end_file_time = time.time()
            file_time = end_file_time - start_file_time
            total_time += file_time

            print(f"Time taken to process {self.__input_filename}: {file_time:.2f} seconds")

        end_time = time.time()
        total_execution_time = end_time - start_time

        print(f"Total time taken to process all PDF files: {total_execution_time:.2f} seconds")


resizer = ResizePDF(
    'J:/arquivos_digitalizados/licenciatura_em_educacao_fisica/em_andamento/licenciatura_em_educacao_fisica_2015(2)/',
    'J:/arquivos_digitalizados/licenciatura_em_educacao_fisica/finalizados/licenciatura_em_educacao_fisica_2015(2)/',
    "A4",
    order_by="name",
    use_custom_order=True
)

#resizer.mm_to_point_transformation()

#resizer.retrieve_pdfs_per_folder()

#resizer.resize() """

resizer.resize_using_custom_order()
resizer.generate_report()