from fpdf import FPDF
import datetime


class PDF(FPDF):
    def header(self):
        date = datetime.datetime.now().date().strftime("%Y-%m-%d")
        self.set_font("Arial", "I", 15)
        self.cell(0, 10, date, 0, 0, "R")
        self.line(10, 10, 186, 10)
        self.ln(10)

    def export(self, conversation: list, username: str):
        self.add_page()
        self.add_font(fname="./fonts/DejaVuSansCondensed.ttf")
        for element in conversation:
            role = username if element["role"] == "user" else element["role"]
            self.set_font("DejaVuSansCondensed", size=16)
            text = role + ": "
            self.cell(0, 7, text, ln=1, align="L")
            self.set_font("DejaVuSansCondensed", size=13)
            self.multi_cell(0, 7, element["content"] + "\n", 0, "J", False)
        return self.output()


# def export_pdf(conversation: list, username: str):
#     pdf = PDF()
#     pdf.add_page()
#     pdf.add_font(fname="./fonts/DejaVuSansCondensed.ttf")
#     for element in conversation:
#         role = username if element["role"] == "user" else element["role"]
#         pdf.set_font("DejaVuSansCondensed", size=16)
#         text = role + ": "
#         pdf.cell(0, 7, text, ln=1, align="L")
#         pdf.set_font("DejaVuSansCondensed", size=13)
#         pdf.multi_cell(0, 7, element["content"] + "\n", 0, "J", False)
#     return pdf.output()
