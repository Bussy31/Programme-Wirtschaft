import tkinter as tk
from tkinter import ttk, messagebox
from fpdf import FPDF
import os


class BuchhaltungsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Profi-Buchhaltungstrainer 2026 - Ultimate Edition")
        self.root.geometry("1050x900")

        self.konten = {}
        self.journal = []

        self.setup_gui()

    def setup_gui(self):
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(expand=1, fill="both", padx=10, pady=10)

        # --- TAB 1: KONTEN & BILANZ-CHECK ---
        self.tab_konten = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_konten, text="1. Konten & Eröffnung")

        frame_kto = tk.LabelFrame(self.tab_konten, text=" Konto eröffnen ", padx=10, pady=10)
        frame_kto.pack(pady=10, fill="x")

        tk.Label(frame_kto, text="Kontoname:").grid(row=0, column=0)
        self.ent_kto_name = tk.Entry(frame_kto)
        self.ent_kto_name.grid(row=0, column=1, padx=5)

        tk.Label(frame_kto, text="AB-Wert (€):").grid(row=0, column=2)
        self.ent_eb_wert = tk.Entry(frame_kto)
        self.ent_eb_wert.grid(row=0, column=3, padx=5)
        self.ent_eb_wert.insert(0, "0")

        tk.Button(frame_kto, text="Aktivkonto (Soll)", command=lambda: self.konto_anlegen("Soll"), bg="#d1ffd1").grid(
            row=0, column=4, padx=2)
        tk.Button(frame_kto, text="Passivkonto (Haben)", command=lambda: self.konto_anlegen("Haben"),
                  bg="#ffd1b3").grid(row=0, column=5, padx=2)

        self.frame_check = tk.Frame(self.tab_konten, relief="groove", borderwidth=2, pady=5)
        self.frame_check.pack(fill="x", padx=10, pady=5)

        self.lbl_aktiv_sum = tk.Label(self.frame_check, text="Summe Aktiv: 0,00 €", fg="green",
                                      font=("Arial", 10, "bold"))
        self.lbl_aktiv_sum.pack(side="left", padx=20)
        self.lbl_passiv_sum = tk.Label(self.frame_check, text="Summe Passiv: 0,00 €", fg="blue",
                                       font=("Arial", 10, "bold"))
        self.lbl_passiv_sum.pack(side="left", padx=20)
        self.lbl_diff = tk.Label(self.frame_check, text="Differenz: 0,00 €", fg="red")
        self.lbl_diff.pack(side="right", padx=20)

        self.tree_konten = ttk.Treeview(self.tab_konten, columns=("Konto", "Soll", "Haben", "Saldo"), show="headings",
                                        height=12)
        for col in ("Konto", "Soll", "Haben", "Saldo"):
            self.tree_konten.heading(col, text=col)
            self.tree_konten.column(col, width=150 if col == "Konto" else 100)
        self.tree_konten.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame1 = tk.Frame(self.tab_konten)
        btn_frame1.pack(pady=5)
        tk.Button(btn_frame1, text="Markiertes Konto bearbeiten", command=self.edit_konto, fg="blue").pack(side="left",
                                                                                                           padx=10)
        tk.Button(btn_frame1, text="Markiertes Konto löschen", command=self.konto_loeschen, fg="red").pack(side="left",
                                                                                                           padx=10)

        # --- TAB 2: JOURNAL ---
        self.tab_journal = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_journal, text="2. Buchen (Journal)")
        frame_buchen = tk.LabelFrame(self.tab_journal, text=" Buchungssatz ", padx=10, pady=10);
        frame_buchen.pack(pady=10, fill="x")
        self.ent_soll = tk.Entry(frame_buchen, width=15);
        self.ent_soll.grid(row=0, column=0)
        tk.Label(frame_buchen, text=" an ").grid(row=0, column=1)
        self.ent_haben = tk.Entry(frame_buchen, width=15);
        self.ent_haben.grid(row=0, column=2)
        tk.Label(frame_buchen, text=" Betrag: ").grid(row=0, column=3)
        self.ent_b_betrag = tk.Entry(frame_buchen, width=10);
        self.ent_b_betrag.grid(row=0, column=4)
        tk.Button(frame_buchen, text="Buchen", command=self.buchen, bg="lightblue").grid(row=0, column=5, padx=10)

        # Neues Journal als Treeview (Tabelle) für einfache Auswahl
        self.tree_journal = ttk.Treeview(self.tab_journal, columns=("Nr", "Soll", "Haben", "Betrag"), show="headings",
                                         height=15)
        for col in ("Nr", "Soll", "Haben", "Betrag"):
            self.tree_journal.heading(col, text=col)
            self.tree_journal.column(col, width=50 if col == "Nr" else 150)
        self.tree_journal.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame2 = tk.Frame(self.tab_journal)
        btn_frame2.pack(pady=5)
        tk.Button(btn_frame2, text="Markierte Buchung bearbeiten", command=self.edit_buchung, fg="blue").pack(
            side="left", padx=10)
        tk.Button(btn_frame2, text="Markierte Buchung löschen", command=self.delete_buchung, fg="red").pack(side="left",
                                                                                                            padx=10)

        # --- TAB 3: EXPORT ---
        self.tab_export = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_export, text="3. Abschluss & PDF")
        tk.Button(self.tab_export, text="PDF Lösung generieren", command=self.export_pdf, font=("Arial", 28, "bold")).pack(pady=100)

    # --- DATEN-MANAGER (Die Zeitmaschine) ---
    def rebuild_accounts(self):
        """Setzt alle Konten auf den AB zurück und bucht das gesamte Journal neu durch."""
        # 1. Konten auf AB zurücksetzen
        for name, daten in self.konten.items():
            daten["Soll"] = [x for x in daten["Soll"] if x[1] == "AB"]
            daten["Haben"] = [x for x in daten["Haben"] if x[1] == "AB"]

        # 2. Journal neu durchbuchen und Nummerierung korrigieren
        new_journal = []
        for idx, (old_nr, s, h, b) in enumerate(self.journal):
            nr = idx + 1  # Nummerierung strikt fortlaufend machen
            new_journal.append((nr, s, h, b))
            self.konten[s]["Soll"].append((b, str(nr), h))
            self.konten[h]["Haben"].append((b, str(nr), s))
        self.journal = new_journal

    # --- UI UPDATES ---
    def update_ui(self):
        # 1. Konten-Tabelle updaten
        for i in self.tree_konten.get_children(): self.tree_konten.delete(i)
        sum_aktiv_ab = 0;
        sum_passiv_ab = 0

        for name, werte in self.konten.items():
            s = sum(item[0] for item in werte["Soll"])
            h = sum(item[0] for item in werte["Haben"])
            self.tree_konten.insert("", "end", iid=name, values=(name, f"{s:.2f}", f"{h:.2f}", f"{abs(s - h):.2f}"))

            if werte["Seite"] == "Soll" and werte["Soll"]: sum_aktiv_ab += werte["Soll"][0][0]
            if werte["Seite"] == "Haben" and werte["Haben"]: sum_passiv_ab += werte["Haben"][0][0]

        # 2. Bilanz-Check updaten
        if len(self.journal) == 0:
            sum_aktiv = sum_aktiv_ab;
            sum_passiv = sum_passiv_ab
        else:
            sum_aktiv = sum(
                max(0, sum(i[0] for i in v["Soll"]) - sum(i[0] for i in v["Haben"])) for v in self.konten.values())
            sum_passiv = sum(
                max(0, sum(i[0] for i in v["Haben"]) - sum(i[0] for i in v["Soll"])) for v in self.konten.values())

        self.lbl_aktiv_sum.config(text=f"Summe Aktiv: {sum_aktiv:,.2f} €")
        self.lbl_passiv_sum.config(text=f"Summe Passiv: {sum_passiv:,.2f} €")
        diff = abs(sum_aktiv - sum_passiv)
        self.lbl_diff.config(text=f"Differenz: {diff:,.2f} €", fg="red" if diff > 0.01 else "green")

        # 3. Journal-Tabelle updaten
        for i in self.tree_journal.get_children(): self.tree_journal.delete(i)
        for nr, s, h, b in self.journal:
            self.tree_journal.insert("", "end", values=(nr, s, h, f"{b:,.2f}"))

    # --- KONTO FUNKTIONEN ---
    def konto_anlegen(self, seite):
        name = self.ent_kto_name.get().strip()
        try:
            wert = float(self.ent_eb_wert.get().replace(",", "."))
            if name:
                if name not in self.konten: self.konten[name] = {"Seite": seite, "Soll": [], "Haben": []}
                if wert > 0: self.konten[name][seite].append((wert, "AB", ""))
                self.update_ui()
                self.ent_kto_name.delete(0, tk.END);
                self.ent_eb_wert.delete(0, tk.END);
                self.ent_eb_wert.insert(0, "0")
                self.ent_kto_name.focus()
        except:
            messagebox.showerror("Fehler", "Zahl eingeben!")

    def konto_loeschen(self):
        sel = self.tree_konten.selection()
        if not sel: return
        name = sel[0]
        # Failsafe: Ist das Konto im Journal schon bebucht?
        in_use = any(s == name or h == name for _, s, h, _ in self.journal)
        if in_use:
            messagebox.showerror("Fehler",
                                 f"Das Konto '{name}' wird bereits im Journal verwendet!\nBitte lösche oder ändere zuerst die Buchungssätze.")
            return
        del self.konten[name]
        self.update_ui()

    def edit_konto(self):
        sel = self.tree_konten.selection()
        if not sel: return
        old_name = sel[0]
        daten = self.konten[old_name]

        # Aktuellen AB auslesen
        ab_val = 0
        if daten["Seite"] == "Soll" and [x for x in daten["Soll"] if x[1] == "AB"]: ab_val = daten["Soll"][0][0]
        if daten["Seite"] == "Haben" and [x for x in daten["Haben"] if x[1] == "AB"]: ab_val = daten["Haben"][0][0]

        win = tk.Toplevel(self.root)
        win.title("Konto bearbeiten")
        win.geometry("300x150")

        tk.Label(win, text="Name:").grid(row=0, column=0, pady=5, padx=5)
        e_name = tk.Entry(win);
        e_name.insert(0, old_name);
        e_name.grid(row=0, column=1)

        tk.Label(win, text="AB-Wert:").grid(row=1, column=0, pady=5, padx=5)
        e_ab = tk.Entry(win);
        e_ab.insert(0, str(ab_val));
        e_ab.grid(row=1, column=1)

        tk.Label(win, text="Seite:").grid(row=2, column=0, pady=5, padx=5)
        c_seite = ttk.Combobox(win, values=["Soll", "Haben"], state="readonly")
        c_seite.set(daten["Seite"]);
        c_seite.grid(row=2, column=1)

        def save():
            new_name = e_name.get().strip()
            try:
                new_ab = float(e_ab.get().replace(",", "."))
            except:
                messagebox.showerror("Fehler", "Ungültiger Betrag"); return
            new_seite = c_seite.get()

            # Wenn der Name geändert wurde, passe das Dictionary und das Journal an
            if new_name != old_name:
                self.konten[new_name] = self.konten.pop(old_name)
                for i in range(len(self.journal)):
                    nr, s, h, b = self.journal[i]
                    if s == old_name: s = new_name
                    if h == old_name: h = new_name
                    self.journal[i] = (nr, s, h, b)

            self.konten[new_name]["Seite"] = new_seite
            # AB Einträge löschen, um sie neu zu setzen
            self.konten[new_name]["Soll"] = [x for x in self.konten[new_name]["Soll"] if x[1] != "AB"]
            self.konten[new_name]["Haben"] = [x for x in self.konten[new_name]["Haben"] if x[1] != "AB"]

            if new_ab > 0: self.konten[new_name][new_seite].insert(0, (new_ab, "AB", ""))

            self.rebuild_accounts();
            self.update_ui();
            win.destroy()

        tk.Button(win, text="Speichern", command=save, bg="green").grid(row=3, columnspan=2, pady=10)

    # --- JOURNAL FUNKTIONEN ---
    def buchen(self):
        s, h = self.ent_soll.get().strip(), self.ent_haben.get().strip()
        try:
            b = float(self.ent_b_betrag.get().replace(",", "."))
            if s in self.konten and h in self.konten:
                nr = len(self.journal) + 1
                self.journal.append((nr, s, h, b))
                self.rebuild_accounts()
                self.update_ui()
                self.ent_soll.delete(0, tk.END);
                self.ent_haben.delete(0, tk.END);
                self.ent_b_betrag.delete(0, tk.END);
                self.ent_soll.focus()
            else:
                messagebox.showwarning("Fehler", "Konto fehlt in Tab 1!")
        except:
            messagebox.showerror("Fehler", "Fehlerhafter Betrag!")

    def delete_buchung(self):
        sel = self.tree_journal.selection()
        if not sel: return
        idx = self.tree_journal.index(sel[0])  # Findet die Position in der Liste
        self.journal.pop(idx)
        self.rebuild_accounts()
        self.update_ui()

    def edit_buchung(self):
        sel = self.tree_journal.selection()
        if not sel: return
        idx = self.tree_journal.index(sel[0])
        nr, s, h, b = self.journal[idx]

        win = tk.Toplevel(self.root)
        win.title("Buchung bearbeiten")
        win.geometry("300x150")

        tk.Label(win, text="Soll:").grid(row=0, column=0, pady=5, padx=5)
        e_s = tk.Entry(win);
        e_s.insert(0, s);
        e_s.grid(row=0, column=1)

        tk.Label(win, text="Haben:").grid(row=1, column=0, pady=5, padx=5)
        e_h = tk.Entry(win);
        e_h.insert(0, h);
        e_h.grid(row=1, column=1)

        tk.Label(win, text="Betrag:").grid(row=2, column=0, pady=5, padx=5)
        e_b = tk.Entry(win);
        e_b.insert(0, str(b));
        e_b.grid(row=2, column=1)

        def save():
            new_s, new_h = e_s.get().strip(), e_h.get().strip()
            try:
                new_b = float(e_b.get().replace(",", "."))
            except:
                messagebox.showerror("Fehler", "Ungültiger Betrag"); return

            if new_s not in self.konten or new_h not in self.konten:
                messagebox.showwarning("Fehler", "Die Konten müssen existieren (siehe Tab 1)!");
                return

            self.journal[idx] = (nr, new_s, new_h, new_b)
            self.rebuild_accounts()
            self.update_ui()
            win.destroy()

        tk.Button(win, text="Speichern", command=save, bg="green").grid(row=3, columnspan=2, pady=10)

    # --- PDF ZEICHENFUNKTIONEN (Wie zuvor) ---
    def draw_bilanz_pdf(self, pdf, title, links, rechts):
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(180, 10, title, ln=True, align="C")
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 8, "Aktiva", border="TLB", align="C")
        pdf.cell(90, 8, "Passiva", border="TRB", align="C", ln=True)

        pdf.set_font("Helvetica", "", 10)
        max_len = max(len(links), len(rechts))
        sum_links = sum(val for _, val in links)
        sum_rechts = sum(val for _, val in rechts)

        for i in range(max_len):
            if i < len(links):
                pdf.cell(60, 6, links[i][0][:25], border="L")
                pdf.cell(30, 6, f"{links[i][1]:,.2f}", border="R", align="R")
            else:
                pdf.cell(90, 6, "", border="LR")

            if i < len(rechts):
                pdf.cell(60, 6, rechts[i][0][:25])
                pdf.cell(30, 6, f"{rechts[i][1]:,.2f}", border="R", align="R", ln=True)
            else:
                pdf.cell(90, 6, "", border="R", ln=True)

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 8, "Summe", border="TLB")
        pdf.cell(30, 8, f"{sum_links:,.2f}", border="TRB", align="R")
        pdf.cell(60, 8, "Summe", border="TLB")
        pdf.cell(30, 8, f"{sum_rechts:,.2f}", border="TRB", align="R", ln=True);
        pdf.ln(10)

    def draw_single_t_konto(self, pdf, x, y, name, werte):
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 8, f"S                            {name[:20]}                            H", border="B", align="C")
        y += 8;
        pdf.set_xy(x, y);
        pdf.set_font("Helvetica", "", 9)
        max_len = max(len(werte["Soll"]), len(werte["Haben"]))

        for i in range(max_len):
            if i < len(werte["Soll"]):
                val, ref, gkto = werte["Soll"][i]
                s_text = f"{ref}) {gkto}" if gkto else str(ref)
                s_val = f"{val:,.2f}"
            else:
                s_text, s_val = "", ""

            if i < len(werte["Haben"]):
                val, ref, gkto = werte["Haben"][i]
                h_text = f"{ref}) {gkto}" if gkto else str(ref)
                h_val = f"{val:,.2f}"
            else:
                h_text, h_val = "", ""

            pdf.cell(27, 6, s_text[:15], border="L")
            pdf.cell(18, 6, s_val, border="R", align="R")
            pdf.cell(27, 6, h_text[:15])
            pdf.cell(18, 6, h_val, border="R", align="R")
            y += 6;
            pdf.set_xy(x, y)

        s_sum = sum(i[0] for i in werte["Soll"]);
        h_sum = sum(i[0] for i in werte["Haben"])
        sb = abs(s_sum - h_sum)

        pdf.set_font("Helvetica", "I", 9)
        if s_sum >= h_sum:
            pdf.cell(45, 6, "", border="LR")
            pdf.cell(20, 6, "SB", align="L")
            pdf.cell(25, 6, f"{sb:,.2f}", border="R", align="R")
        else:
            pdf.cell(20, 6, "SB", border="L", align="L")
            pdf.cell(25, 6, f"{sb:,.2f}", border="R", align="R")
            pdf.cell(45, 6, "", border="R")
        y += 6;
        pdf.set_xy(x, y)

        max_sum = max(s_sum, h_sum)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(20, 6, "", border="TLB")
        pdf.cell(25, 6, f"{max_sum:,.2f}", border="TRB", align="R")
        pdf.cell(20, 6, "", border="TLB")
        pdf.cell(25, 6, f"{max_sum:,.2f}", border="TRB", align="R")
        return y + 10

    def export_pdf(self):
        try:
            pdf = FPDF();
            pdf.add_page()

            eb_aktiv, eb_passiv = [], []
            for name, daten in self.konten.items():
                if daten["Seite"] == "Soll" and daten["Soll"]: eb_aktiv.append((name, daten["Soll"][0][0]))
                if daten["Seite"] == "Haben" and daten["Haben"]: eb_passiv.append((name, daten["Haben"][0][0]))
            self.draw_bilanz_pdf(pdf, "Eröffnungsbilanz", eb_aktiv, eb_passiv)

            pdf.set_font("Helvetica", "B", 12);
            pdf.cell(0, 10, "Grundbuch", ln=True);
            pdf.set_font("Helvetica", "", 10)
            if not self.journal: pdf.cell(0, 6, "(Keine Buchungen)", ln=True)
            for nr, s, h, b in self.journal: pdf.cell(0, 6, f"{nr}) {s} {b:,.2f} an {h} {b:,.2f}", ln=True)
            pdf.ln(10)

            pdf.set_font("Helvetica", "B", 12);
            pdf.cell(0, 10, "Hauptbuch (Aktivkonten links, Passivkonten rechts)", ln=True)
            aktiv_konten = [(k, v) for k, v in self.konten.items() if v["Seite"] == "Soll"]
            passiv_konten = [(k, v) for k, v in self.konten.items() if v["Seite"] == "Haben"]
            max_konten_len = max(len(aktiv_konten), len(passiv_konten))

            for i in range(max_konten_len):
                start_y = pdf.get_y()
                if start_y > 230: pdf.add_page(); start_y = pdf.get_y()
                y_left = start_y;
                y_right = start_y
                if i < len(aktiv_konten): y_left = self.draw_single_t_konto(pdf, 10, start_y, aktiv_konten[i][0],
                                                                            aktiv_konten[i][1])
                if i < len(passiv_konten): y_right = self.draw_single_t_konto(pdf, 105, start_y, passiv_konten[i][0],
                                                                              passiv_konten[i][1])
                pdf.set_y(max(y_left, y_right));
                pdf.set_x(10)

            if pdf.get_y() > 220:
                pdf.add_page()
            else:
                pdf.ln(10)

            sb_aktiv, sb_passiv = [], []
            for name, daten in self.konten.items():
                s_sum = sum(i[0] for i in daten["Soll"]);
                h_sum = sum(i[0] for i in daten["Haben"])
                if s_sum > h_sum:
                    sb_aktiv.append((name, s_sum - h_sum))
                elif h_sum > s_sum:
                    sb_passiv.append((name, h_sum - s_sum))
                elif s_sum > 0:
                    if daten["Seite"] == "Soll":
                        sb_aktiv.append((name, 0.0))
                    else:
                        sb_passiv.append((name, 0.0))
            self.draw_bilanz_pdf(pdf, "Schlussbilanz", sb_aktiv, sb_passiv)

            path = "Buchhaltung_Loesung_Komplett.pdf";
            pdf.output(path)
            if os.name == 'posix':
                os.system(f"open {path}")
            else:
                os.startfile(path)
            messagebox.showinfo("OK", "Lösung erfolgreich exportiert!")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))


if __name__ == "__main__":
    root = tk.Tk();
    app = BuchhaltungsApp(root);
    root.mainloop()