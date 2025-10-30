import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QGroupBox, QSizePolicy, QSpacerItem, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# -------- DATABASE CONFIGURATION (XAMPP MySQL) --------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'imhotep'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# -------- MAIN PORTAL CLASS --------
class ImhotepPortal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imhotep — Pharmacist's Portal")
        self.setGeometry(100, 50, 1000, 750)
        self.setup_ui()

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(12)

        # ---- BACK BUTTON ----
        top_row = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        self.btn_back.setFixedSize(90, 36)
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setStyleSheet("""
            QPushButton { background-color: #ff6666; color: white; border: 1px solid #e74c3c; border-radius: 8px; font-weight: 600; }
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
        outer.addWidget(title, alignment=Qt.AlignHCenter)
        outer.addWidget(subtitle, alignment=Qt.AlignHCenter)
        outer.addSpacing(18)

        # ---- CARD FRAME ----
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(860)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card.setStyleSheet("""
            QFrame#card{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255,255,255,1), stop:1 rgba(250,250,250,1));
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

        # Find Patient Group
        find_group = QGroupBox()
        find_group.setFlat(True)
        find_group.setStyleSheet("QGroupBox { border: none; }")
        fg_layout = QVBoxLayout()
        lbl_find = QLabel("Find Patient")
        lbl_find.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.input_uid = QLineEdit()
        self.input_uid.setPlaceholderText("Enter Patient ID (or leave blank for all)")
        self.input_uid.setFixedHeight(36)
        self.input_uid.setStyleSheet("""
            QLineEdit { padding: 6px; border: 1px solid #ddd; border-radius: 6px; background: #fafafa; }
            QLineEdit:focus { border: 1px solid #7fb3ff; background: #fff; }
        """)
        btn_load = QPushButton("Load Prescription(s)")
        btn_load.setFixedHeight(44)
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_load.setStyleSheet("""
            QPushButton { background-color: #2e86de; color: white; border-radius: 6px; font-weight: 600; padding: 6px 14px; }
            QPushButton:hover { background-color: #2574c8; }
            QPushButton:pressed { background-color: #1f5fa8; }
        """)
        btn_load.clicked.connect(self.on_load)
        fg_layout.addWidget(lbl_find)
        fg_layout.addWidget(self.input_uid)
        fg_layout.addWidget(btn_load)
        find_group.setLayout(fg_layout)

        # Patient details
        details_group = QGroupBox("Patient Details")
        details_group.setFont(QFont("Segoe UI", 11))
        d_layout = QVBoxLayout()
        self.lbl_name = QLabel("Name: —")
        self.lbl_uid = QLabel("UID: —")
        d_layout.addWidget(self.lbl_name)
        d_layout.addWidget(self.lbl_uid)
        d_layout.addStretch(1)
        details_group.setLayout(d_layout)

        # Logout button
        btn_logout = QPushButton("Log Out")
        btn_logout.setFixedHeight(40)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton { background-color: #d9534f; color: white; border-radius: 6px; font-weight: 600; padding: 6px 10px; }
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
        outer.addWidget(card, alignment=Qt.AlignHCenter)
        outer.addSpacerItem(QSpacerItem(0, 16, QSizePolicy.Minimum, QSizePolicy.Expanding))

    # ---------------- DATABASE FUNCTIONS ----------------
    def query_prescriptions_all(self):
        """Fetch distinct prescriptions joined with patient_portal"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT DISTINCT p.Doctor_Sugg, p.Prescription, p.Visit_Date, p.Dispense, pt.User_Name, pt.Patient_ID
                FROM prescription p
                JOIN patient_portal pt ON p.Patient_ID = pt.Patient_ID
            """)
            return cur.fetchall()
        finally:
            conn.close()

    # ---------------- UI HANDLERS ----------------
    def on_load(self):
        prescriptions = self.query_prescriptions_all()
        self.lbl_name.setText("Name: All Patients")
        self.lbl_uid.setText("UID: —")
        self.load_prescriptions(prescriptions)

    def load_prescriptions(self, prescriptions):
        self.clear_prescriptions_area()
        if not prescriptions:
            empty_lbl = QLabel("No prescriptions found.")
            empty_lbl.setStyleSheet("color: #777; font-style: italic;")
            self.right_col.insertWidget(1, empty_lbl)
            return

        for doctor_sugg, prescription_text, visit_date, dispense, patient_name, patient_id in prescriptions:
            info_text = (
                f"Patient: {patient_name} (ID: {patient_id})\n"
                f"Doctor Suggestion: {doctor_sugg}\n"
                f"Dispense Status: {'Active' if dispense else 'Dispensed'}\n"
                f"Visit Date: {visit_date}"
            )
            pres_card = self.create_prescription_card(info_text, prescription_text, patient_id)
            self.right_col.insertWidget(1, pres_card)

    def create_prescription_card(self, info_text, med_text, patient_id):
        card = QFrame()
        card.setStyleSheet("""
            QFrame { border: 1px solid rgba(0,0,0,0.08); border-radius: 10px; background-color: #f7f9f8; }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)

        med_label = QLabel(f"<b>Medication:</b> {med_text}")
        med_label.setFont(QFont("Segoe UI", 10))
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Segoe UI", 9))
        info_label.setStyleSheet("color: #555;")

        btn_dispense = QPushButton("Dispense")
        btn_dispense.setCursor(Qt.PointingHandCursor)
        btn_dispense.setStyleSheet("""
            QPushButton { background-color: #28a745; color: white; border-radius: 6px; font-weight: 600; padding: 4px 10px; }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1e7e34; }
        """)
        btn_dispense.clicked.connect(lambda _, pid=patient_id, card=card: self.on_dispense(pid, card))

        layout.addWidget(med_label)
        layout.addWidget(info_label)
        layout.addWidget(btn_dispense, alignment=Qt.AlignRight)

        return card

    def clear_prescriptions_area(self):
        while self.right_col.count() > 2:
            item = self.right_col.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # ---------------- DISPENSE HANDLER ----------------
    def on_dispense(self, patient_id, card_widget):
        try:
            conn = get_connection()
            cur = conn.cursor()
            # Assuming Dispense = 1 means pending, set to 0 to mark as dispensed
            cur.execute("UPDATE prescription SET Dispense=0 WHERE Patient_ID=%s", (patient_id,))
            conn.commit()
            QMessageBox.information(self, "Dispensed", f"Prescription for Patient ID {patient_id} has been dispensed.")
            card_widget.deleteLater()  # Remove the card from UI
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")
        finally:
            conn.close()

    def on_logout(self):
        self.close()

    def on_back(self):
        QMessageBox.information(self, "Back", "Back button clicked!")

# -------- MAIN EXECUTION --------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ImhotepPortal()
    w.show()
    sys.exit(app.exec_())
