import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QGroupBox, QSizePolicy, QSpacerItem, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# -------- DATABASE CONFIGURATION (for XAMPP MySQL) --------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',        # default user in XAMPP
    'password': '',        # leave empty unless you set a MySQL password
    'database': 'Imhotep'  # must exist in phpMyAdmin
}

def get_connection():
    """Connect to MySQL database via XAMPP."""
    return mysql.connector.connect(**DB_CONFIG)


class ImhotepPortal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep — Pharmacist's Portal")
        self.setMinimumSize(900, 700)
        self.setup_ui()

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # ---- BACK BUTTON ROW ----
        top_row = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        self.btn_back.setFixedSize(90, 36)
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setStyleSheet("""
           QPushButton {
               background-color: #ff6666;   
               color: white;
               border: 1px solid #e74c3c;
               border-radius: 8px;
               font-weight: 600;
           }
           QPushButton:hover { background-color: #ff4d4d; }
           QPushButton:pressed { background-color: #e63939; }
        """)
        self.btn_back.clicked.connect(self.on_back)
        top_row.addWidget(self.btn_back, alignment=Qt.AlignLeft)
        top_row.addStretch(1)
        outer.addLayout(top_row)

        # ---- TITLE ----
        title = QLabel("Imhotep")
        title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        subtitle = QLabel("Pharmacist's Portal")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #777;")

        outer.addSpacing(10)
        outer.addWidget(title, alignment=Qt.AlignHCenter)
        outer.addWidget(subtitle, alignment=Qt.AlignHCenter)
        outer.addSpacing(18)

        # ---- CARD ----
        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(860)
        card.setStyleSheet("""
            QFrame#card{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                                           stop:0 rgba(255,255,255,1), stop:1 rgba(250,250,250,1));
                border-radius: 18px;
                border: 1px solid rgba(0,0,0,0.06);
            }
        """)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(30)

        # ---- LEFT COLUMN ----
        left_col = QVBoxLayout()
        left_col.setSpacing(18)

        # Find Customer group
        find_group = QGroupBox()
        find_group.setFlat(True)
        find_group.setStyleSheet("QGroupBox { border: none; }")
        fg_layout = QVBoxLayout()
        fg_layout.setSpacing(10)
        lbl_find = QLabel("Find Customer")
        lbl_find.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.input_uid = QLineEdit()
        self.input_uid.setPlaceholderText("Enter Customer UID")
        self.input_uid.setFixedHeight(36)
        self.input_uid.setStyleSheet("""
            QLineEdit { padding: 6px; border: 1px solid #ddd; border-radius: 6px; background: #fafafa; }
            QLineEdit:focus { border: 1px solid #7fb3ff; background: #fff; }
        """)

        btn_load = QPushButton("Load Patient Prescription")
        btn_load.setFixedHeight(44)
        btn_load.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_load.clicked.connect(self.on_load)
        btn_load.setStyleSheet("""
            QPushButton {
                background-color: #2e86de;
                color: white;
                border-radius: 6px;
                font-weight: 600;
                padding: 6px 14px;
            }
            QPushButton:hover { background-color: #2574c8; }
            QPushButton:pressed { background-color: #1f5fa8; }
        """)

        fg_layout.addWidget(lbl_find)
        fg_layout.addWidget(self.input_uid)
        fg_layout.addWidget(btn_load)
        find_group.setLayout(fg_layout)

        # Customer details
        details_group = QGroupBox("Customer Details")
        details_group.setFont(QFont("Segoe UI", 11))
        d_layout = QVBoxLayout()
        self.lbl_name = QLabel("Name:")
        self.lbl_uid = QLabel("UID:")
        d_layout.addWidget(self.lbl_name)
        d_layout.addWidget(self.lbl_uid)
        d_layout.addStretch(1)
        details_group.setLayout(d_layout)

        btn_logout = QPushButton("Log Out")
        btn_logout.setFixedHeight(40)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 6px;
                font-weight: 600;
                padding: 6px 10px;
            }
            QPushButton:hover { background-color: #c93f3b; }
        """)
        btn_logout.clicked.connect(self.on_logout)

        left_col.addWidget(find_group)
        left_col.addWidget(details_group)
        left_col.addStretch(1)
        left_col.addWidget(btn_logout, alignment=Qt.AlignLeft)

        # ---- RIGHT COLUMN ----
        self.right_col = QVBoxLayout()
        self.right_col.setSpacing(12)
        pr_label = QLabel("Pending Prescriptions")
        pr_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.right_col.addWidget(pr_label)
        self.right_col.addStretch(1)

        card_layout.addLayout(left_col, 2)
        card_layout.addLayout(self.right_col, 1)
        outer.addWidget(card)
        outer.addSpacerItem(QSpacerItem(0, 16))

    # ---- DB FUNCTIONS ----
    def query_customer(self, uid):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT User_Name FROM Patient_Portal WHERE Patient_ID=%s", (uid,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def query_prescriptions(self, uid):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT Prescription.Pr_ID, Prescription.Prescription, 1 AS quantity,
                       Doctor_Portal.Doctor_Name, Doctor_Portal.Doctor_ID, Prescription.Dispense
                FROM Prescription
                LEFT JOIN Doctor_Portal ON Prescription.Patient_ID = Doctor_Portal.Patient_ID
                WHERE Prescription.Patient_ID=%s AND Prescription.Dispense=1
            """, (uid,))
            rows = cur.fetchall()
            return rows
        finally:
            conn.close()

    # ---- UI EVENT HANDLERS ----
    def on_load(self):
        uid = self.input_uid.text().strip()
        if not uid:
            QMessageBox.warning(self, "Input Error", "Please enter a Customer UID.")
            return

        name = self.query_customer(uid)
        if not name:
            QMessageBox.information(self, "Not Found", "Customer not found in database.")
            self.lbl_name.setText("Name: —")
            self.lbl_uid.setText("UID: —")
            return

        self.lbl_name.setText(f"Name: {name}")
        self.lbl_uid.setText(f"UID: {uid}")

        prescriptions = self.query_prescriptions(uid)
        self.load_prescriptions(prescriptions, name, uid)

    def load_prescriptions(self, prescriptions, name, uid):
        while self.right_col.count() > 2:
            item = self.right_col.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not prescriptions:
            empty_lbl = QLabel("No pending prescriptions.")
            empty_lbl.setStyleSheet("color: #777; font-style: italic;")
            self.right_col.insertWidget(1, empty_lbl)
            return

        for pid, med, qty, doc, docid, _ in prescriptions:
            pres_card = QFrame()
            pres_card.setStyleSheet("""
                QFrame {
                    border: 1px solid rgba(0,0,0,0.08);
                    border-radius: 10px;
                    background-color: #f7f9f8;
                }
            """)
            pres_layout = QVBoxLayout(pres_card)
            pres_layout.setContentsMargins(12, 12, 12, 12)
            pres_layout.setSpacing(8)

            med_line = QLabel(f"<b>Medication:</b> {med} (Qty. {qty})")
            med_line.setFont(QFont("Segoe UI", 10))
            small = QLabel(f"For: {name} (UID: {uid})\nBy: {doc} ({docid})")
            small.setFont(QFont("Segoe UI", 9))
            small.setStyleSheet("color: #555;")

            btn_row = QHBoxLayout()
            btn_row.addStretch(1)
            btn_dispense = QPushButton("Dispense")
            btn_dispense.setFixedHeight(34)
            btn_dispense.setCursor(Qt.PointingHandCursor)
            btn_dispense.setStyleSheet("""
                QPushButton {
                    background-color: #47b881;
                    color: white;
                    border-radius: 6px;
                    font-weight: 600;
                    padding: 6px 12px;
                }
                QPushButton:hover { background-color: #3aa96f; }
            """)
            btn_dispense.clicked.connect(lambda _, pid=pid: self.on_dispense(pid))
            btn_details = QPushButton("Details")
            btn_details.setFixedHeight(34)
            btn_details.setCursor(Qt.PointingHandCursor)
            btn_details.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #333;
                    border: 1px solid #bfc8c4;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
                QPushButton:hover { background-color: #f2f6f4; }
            """)
            btn_details.clicked.connect(lambda _, pid=pid: self.on_details(pid))

            btn_row.addWidget(btn_dispense)
            btn_row.addSpacing(8)
            btn_row.addWidget(btn_details)

            pres_layout.addWidget(med_line)
            pres_layout.addWidget(small)
            pres_layout.addLayout(btn_row)
            self.right_col.insertWidget(1, pres_card)

    def on_dispense(self, pid):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE Prescription SET Dispense=0 WHERE Pr_ID=%s", (pid,))
            conn.commit()
            QMessageBox.information(self, "Success", "Prescription marked as dispensed.")
        finally:
            conn.close()
        self.on_load()

    def on_details(self, pid):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT Prescription.Prescription, 1 AS quantity, Doctor_Portal.Doctor_Name, Doctor_Portal.Doctor_ID
                FROM Prescription
                LEFT JOIN Doctor_Portal ON Prescription.Patient_ID = Doctor_Portal.Patient_ID
                WHERE Pr_ID=%s
            """, (pid,))
            data = cur.fetchone()
            if data:
                med, qty, doc, docid = data
                QMessageBox.information(self, "Prescription Details",
                                        f"Medication: {med}\nQuantity: {qty}\nPrescribed by: {doc} ({docid})")
        finally:
            conn.close()

    def on_logout(self):
        self.close()

    def on_back(self):
        QMessageBox.information(self, "Back", "Back button clicked!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ImhotepPortal()
    w.show()
    sys.exit(app.exec_())
