
import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView

import json
import urllib.request
import urllib.parse
import urllib.error
import threading


class Dashboard:

    def __init__(self, root):
        self.root = root

        self.root.title("ShortestPath AI")
        self.root.geometry("1000x700")
        self.root.minsize(850, 550)
        self.root.configure(bg="#F4F6FA")

        # Koordinat lokasi
        self.point_a = None
        self.point_b = None

        # Marker peta
        self.marker_a = None
        self.marker_b = None

        # Garis rute pada peta
        self.route_paths = []

        # Hasil pencarian lokasi
        self.results_a = []
        self.results_b = []

        self.selected_text = {
            "A": "",
            "B": ""
        }

        self.search_after_a = None
        self.search_after_b = None

        self.create_widgets()

    # =====================================
    # MEMBUAT TAMPILAN UTAMA
    # =====================================
    def create_widgets(self):

        # =================================
        # CANVAS UNTUK SCROLL HALAMAN
        # =================================
        self.main_container = tk.Frame(
            self.root,
            bg="#F4F6FA"
        )
        self.main_container.pack(
            fill="both",
            expand=True
        )

        self.page_canvas = tk.Canvas(
            self.main_container,
            bg="#F4F6FA",
            highlightthickness=0
        )
        self.page_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.page_scrollbar = ttk.Scrollbar(
            self.main_container,
            orient="vertical",
            command=self.page_canvas.yview
        )
        self.page_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.page_canvas.configure(
            yscrollcommand=self.page_scrollbar.set
        )

        # Frame utama yang berada di dalam Canvas
        self.content = tk.Frame(
            self.page_canvas,
            bg="#F4F6FA"
        )

        self.content_window = self.page_canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        # Perbarui area scroll saat ukuran konten berubah
        self.content.bind(
            "<Configure>",
            self.update_scroll_region
        )

        # Sesuaikan lebar konten dengan lebar halaman
        self.page_canvas.bind(
            "<Configure>",
            self.resize_content
        )

        # Aktifkan scroll menggunakan roda mouse
        self.root.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

        # Dukungan scroll untuk Linux
        self.root.bind_all(
            "<Button-4>",
            self.on_mousewheel
        )

        self.root.bind_all(
            "<Button-5>",
            self.on_mousewheel
        )

        # =================================
        # KONTEN HALAMAN
        # =================================
        content = self.content

        # Jarak tepi halaman
        self.page_inner = tk.Frame(
            content,
            bg="#F4F6FA"
        )
        self.page_inner.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        # =================================
        # KARTU PENCARIAN LOKASI
        # =================================
        card = tk.Frame(
            self.page_inner,
            bg="white",
            padx=25,
            pady=20,
            highlightbackground="#E1E6EF",
            highlightthickness=1
        )
        card.pack(fill="x")

        location_frame = tk.Frame(
            card,
            bg="white"
        )
        location_frame.pack(fill="x")

        # =================================
        # LOKASI A
        # =================================
        frame_a = tk.Frame(
            location_frame,
            bg="white"
        )
        frame_a.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 12)
        )

        tk.Label(
            frame_a,
            text="LOKASI AWAL (A)",
            font=("Segoe UI", 10, "bold"),
            fg="#344563",
            bg="white"
        ).pack(anchor="w")

        self.entry_start = ttk.Entry(
            frame_a,
            font=("Segoe UI", 11)
        )
        self.entry_start.pack(
            fill="x",
            ipady=7,
            pady=(7, 0)
        )

        self.listbox_a = tk.Listbox(
            frame_a,
            font=("Segoe UI", 9),
            height=5,
            activestyle="none",
            relief="solid",
            borderwidth=1
        )

        self.entry_start.bind(
            "<KeyRelease>",
            lambda event: self.on_location_typed("A")
        )

        self.listbox_a.bind(
            "<<ListboxSelect>>",
            lambda event: self.select_suggestion("A")
        )

        # =================================
        # LOKASI B
        # =================================
        frame_b = tk.Frame(
            location_frame,
            bg="white"
        )
        frame_b.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(12, 0)
        )

        tk.Label(
            frame_b,
            text="LOKASI TUJUAN (B)",
            font=("Segoe UI", 10, "bold"),
            fg="#344563",
            bg="white"
        ).pack(anchor="w")

        self.entry_destination = ttk.Entry(
            frame_b,
            font=("Segoe UI", 11)
        )
        self.entry_destination.pack(
            fill="x",
            ipady=7,
            pady=(7, 0)
        )

        self.listbox_b = tk.Listbox(
            frame_b,
            font=("Segoe UI", 9),
            height=5,
            activestyle="none",
            relief="solid",
            borderwidth=1
        )

        self.entry_destination.bind(
            "<KeyRelease>",
            lambda event: self.on_location_typed("B")
        )

        self.listbox_b.bind(
            "<<ListboxSelect>>",
            lambda event: self.select_suggestion("B")
        )

        # =================================
        # TOMBOL CARI RUTE
        # =================================
        self.search_button = tk.Button(
            card,
            text="CARI RUTE TERPENDEK",
            font=("Segoe UI", 10, "bold"),
            bg="#315B9A",
            fg="white",
            activebackground="#244778",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.search_route,
            padx=20,
            pady=8
        )
        self.search_button.pack(
            anchor="center",
            pady=(20, 0)
        )

        # =================================
        # INFORMASI HASIL RUTE
        # =================================
        self.route_info_label = tk.Label(
            self.page_inner,
            text="Pilih lokasi awal dan tujuan untuk mencari rute.",
            font=("Segoe UI", 9),
            fg="#344563",
            bg="#F4F6FA",
            anchor="w",
            justify="left",
            wraplength=900
        )
        self.route_info_label.pack(
            fill="x",
            pady=(12, 0)
        )

        # =================================
        # KARTU PETA
        # =================================
        map_card = tk.Frame(
            self.page_inner,
            bg="white",
            highlightbackground="#E1E6EF",
            highlightthickness=1
        )
        map_card.pack(
            fill="x",
            pady=(12, 0)
        )

        tk.Label(
            map_card,
            text="PETA PERJALANAN",
            font=("Segoe UI", 12, "bold"),
            fg="#344563",
            bg="white"
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        self.map_widget = TkinterMapView(
            map_card,
            corner_radius=0,
            height=430
        )
        self.map_widget.pack(
            fill="x",
            expand=False,
            padx=10
        )

        self.map_widget.set_tile_server(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            max_zoom=19
        )

        self.map_widget.set_position(
            -0.0263,
            109.3425
        )

        self.map_widget.set_zoom(13)

        tk.Label(
            map_card,
            text="Map data and imagery: Esri and its data providers.",
            font=("Segoe UI", 7),
            fg="#667085",
            bg="white"
        ).pack(
            anchor="w",
            padx=12,
            pady=(5, 10)
        )

        # =================================
        # TABEL HASIL RUTE
        # DILETAKKAN DI BAWAH PETA
        # =================================
        table_frame = tk.Frame(
            self.page_inner,
            bg="white",
            highlightbackground="#E1E6EF",
            highlightthickness=1
        )
        table_frame.pack(
            fill="x",
            pady=(15, 15)
        )

        tk.Label(
            table_frame,
            text="HASIL PERBANDINGAN RUTE",
            font=("Segoe UI", 11, "bold"),
            fg="#344563",
            bg="white"
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        tk.Label(
            table_frame,
            text="Perbandingan jarak rute utama dengan rute alternatif.",
            font=("Segoe UI", 9),
            fg="#667085",
            bg="white"
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        # Style tabel
        style = ttk.Style()

        style.configure(
            "Route.Treeview",
            font=("Segoe UI", 9),
            rowheight=30,
            background="white",
            fieldbackground="white"
        )

        style.configure(
            "Route.Treeview.Heading",
            font=("Segoe UI", 9, "bold")
        )

        style.map(
            "Route.Treeview",
            background=[("selected", "#DCE8F8")],
            foreground=[("selected", "#23395D")]
        )

        # Frame tabel dan scrollbar
        table_inner = tk.Frame(
            table_frame,
            bg="white"
        )
        table_inner.pack(
            fill="x",
            padx=12,
            pady=(0, 12)
        )

        self.route_table = ttk.Treeview(
            table_inner,
            columns=("rute", "jarak"),
            show="headings",
            height=5,
            style="Route.Treeview"
        )

        self.route_table.heading(
            "rute",
            text="Rute"
        )

        self.route_table.heading(
            "jarak",
            text="Jarak"
        )

        self.route_table.column(
            "rute",
            anchor="w",
            width=650,
            minwidth=250,
            stretch=True
        )

        self.route_table.column(
            "jarak",
            anchor="center",
            width=180,
            minwidth=100,
            stretch=False
        )

        table_scrollbar = ttk.Scrollbar(
            table_inner,
            orient="vertical",
            command=self.route_table.yview
        )

        self.route_table.configure(
            yscrollcommand=table_scrollbar.set
        )

        self.route_table.pack(
            side="left",
            fill="x",
            expand=True
        )

        table_scrollbar.pack(
            side="right",
            fill="y"
        )

        # Keterangan bagian bawah
        tk.Label(
            self.page_inner,
            text="ShortestPath AI - Sistem Pencarian Rute Terpendek",
            font=("Segoe UI", 8),
            fg="#667085",
            bg="#F4F6FA"
        ).pack(
            pady=(0, 10)
        )

    # =====================================
    # MENGATUR AREA SCROLL
    # =====================================
    def update_scroll_region(self, event=None):

        self.page_canvas.configure(
            scrollregion=self.page_canvas.bbox("all")
        )

    def resize_content(self, event):

        self.page_canvas.itemconfigure(
            self.content_window,
            width=event.width
        )

    # =====================================
    # SCROLL MENGGUNAKAN RODA MOUSE
    # =====================================
    def on_mousewheel(self, event):

        # Jangan mengganggu zoom peta ketika mouse
        # sedang berada di area peta.
        try:
            widget = self.root.winfo_containing(
                event.x_root,
                event.y_root
            )

            if widget is not None:

                map_path = str(self.map_widget)

                widget_path = str(widget)

                if (
                    widget_path == map_path
                    or widget_path.startswith(map_path + ".")
                ):
                    return

        except Exception:
            pass

        # Windows
        if event.num == 4:
            self.page_canvas.yview_scroll(-1, "units")

        elif event.num == 5:
            self.page_canvas.yview_scroll(1, "units")

        elif event.delta:

            self.page_canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        return "break"

    # =====================================
    # MEMBATASI WILAYAH KALIMANTAN BARAT
    # =====================================
    def is_in_west_kalimantan(self, latitude, longitude):

        return (
            -3.5 <= latitude <= 2.5
            and 108.0 <= longitude <= 114.5
        )

    # =====================================
    # MENCARI KOORDINAT LOKASI DENGAN PHOTON
    # =====================================
    def get_location_data(self, query):

        params = urllib.parse.urlencode({
            "q": query,
            "limit": 10,
            "lat": -0.0263,
            "lon": 109.3425,
            "zoom": 10,

            # Batas pencarian sekitar Kalimantan Barat
            # Format: minLon, minLat, maxLon, maxLat
            "bbox": "108.0,-3.5,114.5,2.5",

            "countrycode": "ID"
        })

        url = "https://photon.komoot.io/api/?" + params

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ShortestPathAI/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        # Pastikan hasil berada dalam batas wilayah pencarian
        valid_features = []

        for feature in data.get("features", []):

            coordinates = feature.get(
                "geometry", {}
            ).get("coordinates", [])

            if len(coordinates) < 2:
                continue

            longitude = coordinates[0]
            latitude = coordinates[1]

            if self.is_in_west_kalimantan(
                latitude,
                longitude
            ):
                valid_features.append(feature)

        return valid_features

    # =====================================
    # PENCARIAN OTOMATIS
    # =====================================
    def on_location_typed(self, point):

        if point == "A":

            entry = self.entry_start
            listbox = self.listbox_a

            self.point_a = None

            if self.search_after_a:
                self.root.after_cancel(self.search_after_a)

        else:

            entry = self.entry_destination
            listbox = self.listbox_b

            self.point_b = None

            if self.search_after_b:
                self.root.after_cancel(self.search_after_b)

        query = entry.get().strip()

        self.selected_text[point] = ""

        if point == "A" and self.marker_a:

            self.marker_a.delete()
            self.marker_a = None

        elif point == "B" and self.marker_b:

            self.marker_b.delete()
            self.marker_b = None

        self.clear_routes()

        listbox.delete(0, tk.END)
        listbox.place_forget()

        if len(query) < 3:
            return

        if point == "A":

            self.search_after_a = self.root.after(
                700,
                lambda: self.fetch_suggestions(query, point)
            )

        else:

            self.search_after_b = self.root.after(
                700,
                lambda: self.fetch_suggestions(query, point)
            )

    # =====================================
    # MENGAMBIL SARAN LOKASI
    # =====================================
    def fetch_suggestions(self, query, point):

        def worker():

            try:

                features = self.get_location_data(query)

                self.root.after(
                    0,
                    lambda: self.show_suggestions(
                        features,
                        point,
                        query
                    )
                )

            except Exception as error:

                print("Kesalahan pencarian:", error)

                self.root.after(
                    0,
                    lambda: self.show_search_error(point, query)
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # =====================================
    # MENAMPILKAN SARAN LOKASI
    # =====================================
    def show_suggestions(self, features, point, query):

        if point == "A":

            entry = self.entry_start
            listbox = self.listbox_a
            self.results_a = features

        else:

            entry = self.entry_destination
            listbox = self.listbox_b
            self.results_b = features

        if entry.get().strip() != query:
            return

        listbox.delete(0, tk.END)

        for feature in features:

            listbox.insert(
                tk.END,
                self.get_display_name(feature)
            )

        if features:

            listbox.place(
                x=0,
                y=entry.winfo_y() + entry.winfo_height() + 2,
                relwidth=1
            )

            listbox.lift()

        else:

            listbox.place_forget()

    # =====================================
    # MEMBUAT NAMA LOKASI
    # =====================================
    def get_display_name(self, feature):

        properties = feature.get("properties", {})

        name = (
            properties.get("name")
            or properties.get("street")
            or "Lokasi tanpa nama"
        )

        details = []

        for key in [
            "street",
            "district",
            "city",
            "county",
            "state",
            "country"
        ]:

            value = properties.get(key)

            if (
                value
                and value != name
                and value not in details
            ):
                details.append(value)

        if details:

            return name + " - " + ", ".join(details)

        return name

    # =====================================
    # PENCARIAN GAGAL
    # =====================================
    def show_search_error(self, point, query):

        if point == "A":

            entry = self.entry_start
            listbox = self.listbox_a

        else:

            entry = self.entry_destination
            listbox = self.listbox_b

        if entry.get().strip() == query:

            listbox.delete(0, tk.END)
            listbox.place_forget()

    # =====================================
    # MENYIMPAN LOKASI DAN MARKER
    # =====================================
    def set_location(self, point, feature):

        coordinates = feature.get(
            "geometry", {}
        ).get("coordinates", [])

        if len(coordinates) < 2:
            return False

        longitude = coordinates[0]
        latitude = coordinates[1]

        if not self.is_in_west_kalimantan(
            latitude,
            longitude
        ):

            messagebox.showwarning(
                "Lokasi di Luar Wilayah",
                "Pilih lokasi yang berada di Kalimantan Barat."
            )

            return False

        display_name = self.get_display_name(feature)

        if point == "A":

            self.point_a = (latitude, longitude)
            entry = self.entry_start

            if self.marker_a:
                self.marker_a.delete()

            self.marker_a = self.map_widget.set_marker(
                latitude,
                longitude,
                text="A - Lokasi Awal"
            )

            self.listbox_a.place_forget()

        else:

            self.point_b = (latitude, longitude)
            entry = self.entry_destination

            if self.marker_b:
                self.marker_b.delete()

            self.marker_b = self.map_widget.set_marker(
                latitude,
                longitude,
                text="B - Lokasi Tujuan"
            )

            self.listbox_b.place_forget()

        entry.delete(0, tk.END)
        entry.insert(0, display_name)

        self.selected_text[point] = display_name

        self.clear_routes()

        if self.point_a is not None and self.point_b is not None:

            self.map_widget.fit_bounding_box(
                self.point_a,
                self.point_b
            )

        else:

            self.map_widget.set_position(
                latitude,
                longitude
            )

            self.map_widget.set_zoom(15)

        return True

    # =====================================
    # MEMILIH SARAN LOKASI
    # =====================================
    def select_suggestion(self, point):

        if point == "A":

            listbox = self.listbox_a
            features = self.results_a

        else:

            listbox = self.listbox_b
            features = self.results_b

        selection = listbox.curselection()

        if not selection:
            return

        index = selection[0]

        if index >= len(features):
            return

        self.set_location(
            point,
            features[index]
        )

    # =====================================
    # MENGHAPUS GARIS RUTE DAN TABEL LAMA
    # =====================================
    def clear_routes(self):

        for path in self.route_paths:

            try:
                path.delete()

            except Exception:
                pass

        self.route_paths = []

        self.route_info_label.config(
            text="Pilih lokasi awal dan tujuan untuk mencari rute."
        )

        # Kosongkan tabel
        if hasattr(self, "route_table"):

            for item in self.route_table.get_children():

                self.route_table.delete(item)

    # =====================================
    # MENCARI RUTE MENGGUNAKAN OSRM
    # =====================================
    def get_routes(self, start, destination):

        # OSRM menggunakan urutan longitude,latitude
        start_lon = start[1]
        start_lat = start[0]

        end_lon = destination[1]
        end_lat = destination[0]

        coordinates = (
            f"{start_lon},{start_lat};"
            f"{end_lon},{end_lat}"
        )

        params = urllib.parse.urlencode({
            "alternatives": "true",
            "steps": "false",
            "overview": "full",
            "geometries": "geojson"
        })

        url = (
            "https://router.project-osrm.org/route/v1/driving/"
            + coordinates
            + "?"
            + params
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ShortestPathAI/1.0"
            }
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=40
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as error:

            detail = error.read().decode(
                "utf-8",
                errors="replace"
            )

            raise Exception(
                f"Server OSRM menolak permintaan "
                f"(HTTP {error.code}). {detail}"
            )

        if data.get("code") != "Ok":

            raise Exception(
                data.get("message", "Rute tidak ditemukan.")
            )

        return data.get("routes", [])

    # =====================================
    # TOMBOL CARI RUTE
    # =====================================
    def search_route(self):

        start = self.entry_start.get().strip()
        destination = self.entry_destination.get().strip()

        if not start or not destination:

            messagebox.showwarning(
                "Peringatan",
                "Lokasi awal dan tujuan harus diisi."
            )

            return

        self.search_button.config(
            state="disabled",
            text="MENCARI RUTE..."
        )

        self.route_info_label.config(
            text="Sedang mencari rute utama dan alternatif..."
        )

        def worker():

            try:

                point_a = self.point_a
                point_b = self.point_b

                # Cari koordinat lokasi A jika belum dipilih
                if point_a is None:

                    features_a = self.get_location_data(start)

                    if not features_a:

                        raise Exception(
                            f"Lokasi awal '{start}' tidak ditemukan "
                            "di wilayah pencarian Kalimantan Barat."
                        )

                    coordinates_a = features_a[0]["geometry"]["coordinates"]

                    point_a = (
                        coordinates_a[1],
                        coordinates_a[0]
                    )

                # Cari koordinat lokasi B jika belum dipilih
                if point_b is None:

                    features_b = self.get_location_data(destination)

                    if not features_b:

                        raise Exception(
                            f"Lokasi tujuan '{destination}' tidak ditemukan "
                            "di wilayah pencarian Kalimantan Barat."
                        )

                    coordinates_b = features_b[0]["geometry"]["coordinates"]

                    point_b = (
                        coordinates_b[1],
                        coordinates_b[0]
                    )

                # Validasi wilayah sebelum meminta rute
                if not self.is_in_west_kalimantan(
                    point_a[0],
                    point_a[1]
                ):

                    raise Exception(
                        "Lokasi awal berada di luar wilayah pencarian "
                        "Kalimantan Barat."
                    )

                if not self.is_in_west_kalimantan(
                    point_b[0],
                    point_b[1]
                ):

                    raise Exception(
                        "Lokasi tujuan berada di luar wilayah pencarian "
                        "Kalimantan Barat."
                    )

                routes = self.get_routes(
                    point_a,
                    point_b
                )

                self.root.after(
                    0,
                    lambda: self.finish_route_search(
                        start,
                        destination,
                        point_a,
                        point_b,
                        routes
                    )
                )

            except Exception as error:

                print("Kesalahan pencarian rute:", error)

                error_message = str(error)

                self.root.after(
                    0,
                    lambda message=error_message:
                    self.route_search_failed(message)
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # =====================================
    # MENAMPILKAN HASIL RUTE
    # =====================================
    def finish_route_search(
        self,
        start,
        destination,
        point_a,
        point_b,
        routes
    ):

        self.search_button.config(
            state="normal",
            text="CARI RUTE TERPENDEK"
        )

        # Pastikan input belum berubah selama pencarian
        if (
            self.entry_start.get().strip() != start
            or self.entry_destination.get().strip() != destination
        ):
            return

        if not routes:

            messagebox.showwarning(
                "Rute Tidak Ditemukan",
                "Tidak ada rute jalan yang ditemukan antara kedua lokasi."
            )

            return

        self.point_a = point_a
        self.point_b = point_b

        # Hapus marker lama
        if self.marker_a:
            self.marker_a.delete()

        if self.marker_b:
            self.marker_b.delete()

        # Marker lokasi awal dan tujuan
        self.marker_a = self.map_widget.set_marker(
            point_a[0],
            point_a[1],
            text="A - Lokasi Awal"
        )

        self.marker_b = self.map_widget.set_marker(
            point_b[0],
            point_b[1],
            text="B - Lokasi Tujuan"
        )

        self.clear_routes()

        # =================================
        # FILTER RUTE YANG VALID
        # =================================
        valid_routes = []

        for route in routes:

            coordinates = route.get(
                "geometry", {}
            ).get("coordinates", [])

            if len(coordinates) >= 2:
                valid_routes.append(route)

        if not valid_routes:

            messagebox.showwarning(
                "Rute Tidak Ditemukan",
                "Data rute tidak memiliki geometri jalan "
                "yang bisa ditampilkan."
            )

            return

        # =================================
        # URUTKAN RUTE BERDASARKAN JARAK
        # =================================
        valid_routes.sort(
            key=lambda route: route.get(
                "distance",
                float("inf")
            )
        )

        route_details = []

        route_colors = [
            "#E53935",
            "#F28C28",
            "#1976D2",
            "#8E44AD",
            "#009688",
            "#795548"
        ]

        # =================================
        # MENAMPILKAN RUTE DAN MENGISI TABEL
        # =================================
        for index, route in enumerate(valid_routes):

            coordinates = route.get(
                "geometry", {}
            ).get("coordinates", [])

            # GeoJSON OSRM: longitude, latitude
            # TkinterMapView: latitude, longitude
            path_positions = [
                (coordinate[1], coordinate[0])
                for coordinate in coordinates
            ]

            color = route_colors[
                index % len(route_colors)
            ]

            width = 6 if index == 0 else 4

            path = self.map_widget.set_path(
                path_positions,
                color=color,
                width=width
            )

            self.route_paths.append(path)

            distance_km = (
                route.get("distance", 0) / 1000
            )

            duration_minutes = (
                route.get("duration", 0) / 60
            )

            # Nama pada tabel
            if index == 0:

                route_name = (
                    f"{start}, {destination}"
                )

            else:

                route_name = (
                    f"{start}, {destination} "
                    f"(Alternatif {index})"
                )

            # Masukkan rute dan jarak ke tabel
            self.route_table.insert(
                "",
                tk.END,
                values=(
                    route_name,
                    f"{distance_km:.2f} km"
                )
            )

            # Informasi tambahan
            status = (
                " - PILIHAN GREEDY"
                if index == 0
                else ""
            )

            route_details.append(
                f"Rute {index + 1}: "
                f"{distance_km:.2f} km | "
                f"{duration_minutes:.0f} menit"
                f"{status}"
            )

        # =================================
        # INFORMASI RUTE TERPENDEK
        # =================================
        shortest_route = valid_routes[0]

        shortest_distance = (
            shortest_route.get("distance", 0) / 1000
        )

        shortest_duration = (
            shortest_route.get("duration", 0) / 60
        )

        information = (
            f"Alternatif ditemukan: {len(valid_routes)} rute\n"
            f"Rute terpendek: {shortest_distance:.2f} km "
            f"({shortest_duration:.0f} menit)\n"
            + "\n".join(route_details)
        )

        self.route_info_label.config(
            text=information
        )

        # Tampilkan keseluruhan rute pada peta
        self.map_widget.fit_bounding_box(
            point_a,
            point_b
        )

        # Perbarui area scroll setelah hasil dimuat
        self.content.update_idletasks()
        self.update_scroll_region()

        messagebox.showinfo(
            "Hasil Pencarian Rute",
            "Pencarian rute berhasil!\n\n"
            f"Jumlah alternatif: {len(valid_routes)}\n"
            f"Rute terpendek: {shortest_distance:.2f} km\n"
            f"Estimasi waktu: {shortest_duration:.0f} menit\n\n"
            "Garis merah = pilihan Greedy (jarak terpendek)\n"
            "Warna lainnya = rute alternatif\n\n"
            "Catatan: jumlah alternatif bergantung pada "
            "rute yang tersedia dari layanan OSRM."
        )

    # =====================================
    # MENANGANI KEGAGALAN PENCARIAN RUTE
    # =====================================
    def route_search_failed(self, error):

        self.search_button.config(
            state="normal",
            text="CARI RUTE TERPENDEK"
        )

        self.route_info_label.config(
            text="Rute belum berhasil ditemukan."
        )

        messagebox.showerror(
            "Pencarian Rute Gagal",
            "Sistem belum berhasil menemukan rute.\n\n"
            f"Keterangan: {error}\n\n"
            "Periksa koneksi internet atau coba lokasi lain."
        )

