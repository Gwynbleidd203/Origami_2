from dataclasses import dataclass
import os
import pypdf
import time
from progress.bar import Bar
from typing import Literal, List
from multiprocessing import Pool, cpu_count
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
        filename = file or self.__input_filename
        return filename.split('.')[-1].lower() == self.__desired_doc_type

    def retrieve_custom_pdfs(self) -> List[RetrievedFilesType]:
        document_list = []
        for doc in self.read_order_from_file():
            created_at, last_modified_at = self.get_doc_info(doc)
            document_list.append(
                RetrievedFilesType(
                    name=os.path.basename(doc),
                    path=doc,
                    created_at=created_at,
                    last_modified_at=last_modified_at
                )
            )
        return document_list

    def retrieve_pdfs_per_folder(self) -> List[RetrievedFilesType]:
        document_list = os.listdir(self.__input_path)
        pdf_list = []
        for doc in document_list:
            if self.is_pdf(doc):
                created_at, last_modified_at = self.get_doc_info(f'{self.__input_path}{doc}')
                pdf_list.append(
                    RetrievedFilesType(
                        name=doc,
                        path=f'{self.__input_path}{doc}',
                        created_at=created_at,
                        last_modified_at=last_modified_at
                    )
                )
        ordenated_pdf_list = self.ordenate_files(pdf_list)
        self.write_order_in_txt(ordenated_pdf_list)
        return ordenated_pdf_list

    def ordenate_files(self, pdf_list: List[RetrievedFilesType]) -> List[RetrievedFilesType]:
        if self.__order_by == "name":
            return sorted(pdf_list, key=lambda x: x.name)
        elif self.__order_by == "creation_date":
            return sorted(pdf_list, key=lambda x: x.created_at)
        elif self.__order_by == "last_modification_date":
            return sorted(pdf_list, key=lambda x: x.last_modified_at)
        else:
            return pdf_list

    def write_order_in_txt(self, pdf_list: List[RetrievedFilesType], complete_path: bool = True) -> None:
        with open(self.__CUSTOM_ORDER_PATH, 'w') as file:
            for doc in pdf_list:
                document_name = doc.path if complete_path else doc.name
                file.write(f'{document_name}\n')

    def read_order_from_file(self) -> List[str]:
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
        return order_list

    def print_documents(self, pdf_list: List[RetrievedFilesType]) -> None:
        print("List of Retrieved PDF Documents:")
        print("{:<30} {:<50} {:<20} {:<20}".format("Name", "Path", "Created At", "Last Modified At"))
        print("-" * 120)
        for doc in pdf_list:
            print("{:<30} {:<50} {:<20} {:<20}".format(doc.name, doc.path, doc.created_at, doc.last_modified_at))

    def get_doc_info(self, path: str) -> tuple[str, str]:
        creation_time = os.path.getctime(path)
        lastmodified_time = os.path.getmtime(path)
        return time.ctime(creation_time), time.ctime(lastmodified_time)

    def mm_to_point_transformation(self) -> tuple[float, float]:
        final_width = round(self.__formats[self.__desired_format][0] * self.__MEASEURE_POINTS, 3)
        final_height = round(self.__formats[self.__desired_format][1] * self.__MEASEURE_POINTS, 3)
        return final_width, final_height

    def get_scale_factor(self, original_dimension: tuple[float, float]) -> tuple[float, float]:
        width_scale_factor = self.__desired_dimensions[0] / original_dimension[0]
        height_scale_factor = self.__desired_dimensions[1] / original_dimension[1]
        return width_scale_factor, height_scale_factor

    def __handle_resize(self, pdf_file_path: str, output_path: str):
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
                    if original_dimension == self.__desired_dimensions:
                        writer.add_page(page)
                        continue
                    scale_factor = self.get_scale_factor(original_dimension)
                    page.scale(scale_factor[0], scale_factor[1])
                    page.mediabox.lower_left = (0, 0)
                    page.mediabox.upper_right = self.__desired_dimensions
                    writer.add_page(page)
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
            print(f'{bcolors.OKGREEN}The PDF file ({self.__input_filename}) has been resized with success!')
        except Exception as error:
            print(f'{bcolors.FAIL}An error occurred: ', error)

    def resize_pipeline(self, pdf_list: List[RetrievedFilesType]) -> None:
        print(f'{bcolors.OKBLUE}Converting {len(pdf_list)} files...')
        progress_bar = Bar(f'{bcolors.OKBLUE}Processing {self.__input_filename}...', max=len(pdf_list))
        
        def process_document(doc):
            self.__input_filename = doc.name
            self.__handle_resize(doc.path, self.__output_path + self.__input_filename)
        
        with Pool(cpu_count()) as pool:
            for _ in pool.imap_unordered(process_document, pdf_list):
                progress_bar.next()
        
        progress_bar.finish()

    def resize_a_single_file(self) -> None:
        if self.is_pdf(self.__input_filename):
            self.__handle_resize(self.__input_path, self.__output_path)
        else:
            print(f'{bcolors.FAIL}The file ({self.__input_filename}) is not a PDF or is not supported.')

    def resize_using_custom_order(self) -> None:
        custom_list = self.retrieve_custom_pdfs()
        print(f'{bcolors.HEADER}Checking for files veracity...')
        print('\n' * os.get_terminal_size().lines)
        for item in custom_list:
            self.__input_filename = item.name
            self.__handle_resize(item.path, self.__output_path + self.__input_filename)

    def resize(self) -> None:
        if os.path.isfile(self.__input_path):
            self.resize_a_single_file()
        elif os.path.isdir(self.__input_path):
            pdf_list = self.retrieve_pdfs_per_folder()
            if len(pdf_list) == 1:
                self.resize_a_single_file(pdf_list[0])
            elif len(pdf_list) > 1:
                self.resize_pipeline(pdf_list)
            else:
                print(f"{bcolors.WARNING}No PDF files found in the directory.")
        else:
            print(f"{bcolors.WARNING}Invalid input path.")

    def generate_report(self):
        start_time = time.time()
        pdf_list = self.retrieve_pdfs_per_folder()
        num_pdfs = len(pdf_list)
        print(f"Number of PDF files processed: {num_pdfs}")
        total_time = 0
        for doc in pdf_list:
            start_file_time = time.time()
            self.__input_filename = doc.name
            self.__handle_resize(doc.path, self.__output_path + self.__input_filename)
            end_file_time = time.time()
            file_time = end_file_time - start_file_time
            total_time += file_time
            print(f"Time taken to process {self.__input_filename}: {file_time:.2f} seconds")
        end_time = time.time()
        total_execution_time = end_time - start_time
        print(f"Total time taken to process all PDF files: {total_execution_time:.2f} seconds")

resizer = ResizePDF(
    'J:/arquivos_digitalizados/licenciatura_em_educacao_fisica/em_andamento/licenciatura_em_educacao_fisica_2022(2)/',
    'J:/arquivos_digitalizados/licenciatura_em_educacao_fisica/finalizados/licenciatura_em_educacao_fisica_2022(2)/',
    "A4",
    order_by="last_modification_date",
    use_custom_order=True
)

# Uncomment the function you want to execute
resizer.retrieve_pdfs_per_folder()
# resizer.resize()
# resizer.resize_using_custom_order()
# resizer.generate_report()
