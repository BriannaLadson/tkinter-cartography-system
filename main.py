from tkinter import *
from tkinter import ttk
import random
from cqcalendar import CQCalendar

def process_cmd(play_screen, cmd):
	try:
		cmd_dict[cmd](play_screen, cmd)
		
		play_screen.game.inc_time()
		
		discovered_locations = play_screen.game.update_characters()
		play_screen.update_screen()
		
		for location in discovered_locations:
			DiscoveredLocationPopup(play_screen.root, location)
	
	except KeyError:
		pass
		
def move_cmd(play_screen, cmd):
	tile_map = play_screen.tile_map
	
	try:
		getattr(tile_map, f"move_{cmd}")()
	
	except AttributeError:
		pass
		
def shop_cmd(play_screen, cmd):
	game = play_screen.game
	player = game.player
	
	location = game.locations.get((player.x, player.y))
	
	if location is not None and location.location_type in ["Town", "Village"]:
		ShopPopup(play_screen.root, location)
		
cmd_dict = {
	"up": move_cmd,
	"northwest": move_cmd,
	"northeast": move_cmd,
	"down": move_cmd,
	"southwest": move_cmd,
	"southeast": move_cmd,
	"left": move_cmd,
	"right": move_cmd,
	"shop": shop_cmd,
}

class Root(Tk):
	def __init__(self):
		super().__init__()
		self.state("zoomed")
		
		self.game = game = Game()
		
		self.play_screen = PlayScreen(self, game)
		self.play_screen.pack(fill=BOTH, expand=1)
		
class PlayScreen(ttk.Frame):
	def __init__(self, root, game):
		super().__init__(root)
		
		self.root = root
		
		self.game = game
		
		self.calendar = game.calendar
		
		self.player = player = game.player
		
		left_fr = ttk.Frame(self)
		left_fr.pack(side=LEFT, fill=Y)
		
		self.status_fr = StatusFrame(left_fr, root, game)
		self.status_fr.pack(fill=BOTH, expand=1)
		
		right_fr = ttk.Frame(self)
		right_fr.pack(side=LEFT, fill=BOTH, expand=1)
		
		#Calendar
		self.time_var = StringVar(value=f"Time: {self.calendar.time_string()}")
		
		time_lbl = ttk.Label(right_fr, textvariable=self.time_var, anchor="center")
		time_lbl.pack(fill=X)
		
		self.date_var = StringVar(value=f"Date: {self.calendar.date_string()}")
		
		date_lbl = ttk.Label(right_fr, textvariable=self.date_var, anchor="center")
		date_lbl.pack(fill=X)
		
		#Location
		self.location_var = StringVar(value=f"Location: {player.x},{player.y}")
		
		location_lbl = ttk.Label(right_fr, textvariable=self.location_var, anchor="center")
		location_lbl.pack(fill=X)
		
		#Tile Map
		self.tile_map = TileMap(right_fr, game)
		self.tile_map.pack(fill=BOTH, expand=1)
		
		#Bindings
		root.bind("<+>", self.tile_map.zoom_in)
		root.bind("<minus>", self.tile_map.zoom_out)
		
		root.bind("<Up>", lambda event:process_cmd(self, "up"))
		root.bind("8", lambda event:process_cmd(self, "up"))
		
		root.bind("7", lambda event:process_cmd(self, "northwest"))
		
		root.bind("9", lambda event:process_cmd(self, "northeast"))
		
		root.bind("<Down>", lambda event:process_cmd(self, "down"))
		root.bind("2", lambda event:process_cmd(self, "down"))
		
		root.bind("1", lambda event:process_cmd(self, "southwest"))
		
		root.bind("3", lambda event:process_cmd(self, "southeast"))
		
		root.bind("<Left>", lambda event:process_cmd(self, "left"))
		root.bind("4", lambda event:process_cmd(self, "left"))
		
		root.bind("<Right>", lambda event:process_cmd(self, "right"))
		root.bind("6", lambda event:process_cmd(self, "right"))
		
		root.bind("5", lambda event: process_cmd(self, "shop"))
		
		self.update_screen()
		
	def update_screen(self):
		self.update_calendar()
		
		self.update_location()
		
		self.status_fr.update_frame()
		
	def update_calendar(self):
		self.time_var.set(f"Time: {self.calendar.time_string()}")
		self.date_var.set(f"Date: {self.calendar.date_string()}")
		
	def update_location(self):
		player = self.player
	
		self.location_var.set(f"Location: {player.x},{player.y}")
		
class TileMap(Canvas):
	def __init__(self, parent, game):
		super().__init__(parent, highlightbackground="black", highlightthickness=2)
		
		self.game = game
		
		self.player = game.player
		
		self.min_tiles = 11
		self.max_tiles = 51
		
		self.map_size = 11
		
		self.tiles = []
		
		self.bind("<Configure>", self.update_map)
		
	def zoom_in(self, event=None):
		self.map_size -= 2
		
		if self.map_size < self.min_tiles:
			self.map_size = self.min_tiles
			
		self.tiles = []
		
		self.update_map()
		
	def zoom_out(self, event=None):
		self.map_size += 2
		
		if self.map_size > self.max_tiles:
			self.map_size = self.max_tiles
			
		self.tiles = []
		
		self.update_map()
		
	def update_map(self, event=None):
		self.update_idletasks()
		
		self.draw_tiles()
		
		self.draw_locations()
		
		self.draw_npcs()
		
		self.draw_player()
		
	def draw_tiles(self):
		canvas_width = self.winfo_width()
		canvas_height = self.winfo_height()
		
		tile_width = canvas_width / self.map_size
		tile_height = canvas_height / self.map_size
		
		if not self.tiles:
			self.delete("tile")
			
			for sy in range(self.map_size):
				row = []
				
				for sx in range(self.map_size):
					tx = sx * tile_width
					ty = sy * tile_height
					
					rect = self.create_rectangle(
						tx, ty,
						tx + tile_width, ty + tile_height,
						tags="tile",
						width=2,
					)
					
					row.append(rect)
					
				self.tiles.append(row)
				
		half = self.map_size // 2
		
		px = self.player.x
		py = self.player.y
				
		for sy in range(self.map_size):
			for sx in range(self.map_size):
				wx = px - half + sx
				wy = py - half + sy
				
				tx = sx * tile_width
				ty = sy * tile_height
				
				rect = self.tiles[sy][sx]
				
				self.coords(
					rect,
					tx, ty,
					tx + tile_width, ty + tile_height,
				)
				
				if 0 <= wx < self.game.world_size and 0 <= wy < self.game.world_size:
					color = "white"
					
				else:
					color = "black"
					
				self.itemconfigure(rect, fill=color)
				
	def draw_locations(self):
		if hasattr(self, "location_items"):
			for item in self.location_items:
				self.delete(item)

		self.location_items = []

		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size

		half = self.map_size // 2
		
		px = self.player.x
		py = self.player.y

		for sy in range(self.map_size):
			for sx in range(self.map_size):
				wx = px - half + sx
				wy = py - half + sy

				if not (0 <= wx < self.game.world_size and 0 <= wy < self.game.world_size):
					continue

				location = self.player.known_locations.get((wx, wy))

				if location is None:
					continue

				cx = (sx + 0.5) * tile_width
				cy = (sy + 0.5) * tile_height

				font_size = int(min(tile_width, tile_height) * 0.5)

				item = self.create_text(
					cx, cy,
					text=location.char,
					font=("TkDefaultFont", font_size, "bold")
				)

				self.location_items.append(item)
				self.tag_raise(item)
				
	def draw_player(self):
		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size
		
		center = self.map_size // 2
		
		cx = (center + 0.5) * tile_width
		cy = (center + 0.5) * tile_height
		
		font_size = int(min(tile_width, tile_height) * 0.5)
		
		if not hasattr(self, "player_item"):
			self.player_item = self.create_text(
				cx, cy,
				text=self.player.char,
				font=("TkDefaultFont", font_size, "bold")
			)
			
		else:
			self.coords(self.player_item, cx, cy)
			self.itemconfig(self.player_item, font=("TkDefaultFont", font_size, "bold"))
			
		self.tag_raise(self.player_item)
		
	def draw_npcs(self):
		if hasattr(self, "npc_items"):
			for item in self.npc_items:
				self.delete(item)
				
		self.npc_items = []
		
		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size

		half = self.map_size // 2
		
		px = self.player.x
		py = self.player.y
		
		for npc in self.game.cartographers:
			wx = npc.x
			wy = npc.y
			
			sx = wx - px + half
			sy = wy - py + half
			
			if not (0 <= sx < self.map_size and 0 <= sy < self.map_size):
				continue
				
			cx = (sx + 0.5) * tile_width
			cy = (sy + 0.5) * tile_height
			
			font_size = int(min(tile_width, tile_height) * 0.5)
			
			item = self.create_text(
				cx, cy,
				text=npc.char,
				font=("TkDefaultFont", font_size, "bold"),
				fill="blue",
			)
			
			self.npc_items.append(item)
			self.tag_raise(item)
		
	def move_left(self, event=None):
		if self.player.x > 0:
			self.player.x -= 1
			
			self.update_map()
			
	def move_right(self, event=None):
		if self.player.x < self.game.world_size - 1:
			self.player.x += 1
			
			self.update_map()
			
	def move_up(self, event=None):
		if self.player.y > 0:
			self.player.y -= 1
			
			self.update_map()
			
	def move_northwest(self, event=None):
		if self.player.x > 0 and self.player.y > 0:
			self.player.x -= 1
			self.player.y -= 1
			
			self.update_map()
	
	def move_northeast(self, event=None):
		if self.player.x < self.game.world_size - 1 and self.player.y > 0:
			self.player.x += 1
			self.player.y -= 1
			
			self.update_map()
	
	def move_down(self, event=None):
		if self.player.y < self.game.world_size - 1:
			self.player.y += 1
			
			self.update_map()
			
	def move_southwest(self, event=None):
		if self.player.x > 0 and self.player.y < self.game.world_size - 1:
			self.player.x -= 1
			self.player.y += 1
			
			self.update_map()
			
	def move_southeast(self, event=None):
		if self.player.x < self.game.world_size - 1 and self.player.y < self.game.world_size - 1:
			self.player.x += 1
			self.player.y += 1
			
			self.update_map()
			
class Popup(Toplevel):
	def __init__(self, root):
		super().__init__(root)
		
		self.root = root
		
		self.overrideredirect(True)
		
		self.grab_set()
		
	def center(self):
		self.update_idletasks()
		
		sw = self.winfo_screenwidth()
		sh = self.winfo_screenheight()
		
		tw = self.winfo_width()
		th = self.winfo_height()
		
		x = (sw // 2) - (tw // 2)
		y = (sh // 2) - (th // 2)
		
		self.geometry(f"{tw}x{th}+{x}+{y}")
		
class DiscoveredLocationPopup(Popup):
	def __init__(self, root, location):
		super().__init__(root)
		
		lbl = ttk.Label(self, text=f"You discovered a {location.location_type.lower()} named {location.name}!")
		lbl.pack()
		
		ok_btn = ttk.Button(self, text="OK", command=self.destroy)
		ok_btn.pack()
		
		self.center()
		
class CreateMapPopup(Popup):
	def __init__(self, root):
		super().__init__(root)
		
		self.root = root
		
		self.game = game = root.game
		
		self.player = player = game.player
		
		if not self.player.known_locations:
			lbl = ttk.Label(self, text="You must discover a location before you can create a map!", anchor="center")
			lbl.pack()
			
			btn = ttk.Button(self, text="OK", command=self.destroy)
			btn.pack()
			
		else:
			self.location_var = StringVar()
			
			self.locations = sorted(
				self.player.known_locations.values(),
				key=lambda location: location.name
			)
			
			location_names = [
				f"{location.name} ({location.location_type}) {location.x, location.y}" for location in self.locations
			]
			
			max_length = max(len(name) for name in location_names)
			
			self.location_cbx = ttk.Combobox(self, textvariable=self.location_var, values=location_names, state="readonly", width=max_length)
			self.location_cbx.pack(fill=X, padx=10, pady=10)
			
			if location_names:
				self.location_cbx.current(0)
				
			self.create_btn = ttk.Button(self, text="Create Map", command=self.create_map)
			self.create_btn.pack(fill=X, pady=(10, 0))
			
			self.cancel_btn = ttk.Button(self, text="Cancel", command=self.destroy)
			self.cancel_btn.pack(fill=X)
			
		self.center()
		
	def create_map(self):
		root = self.root
		game = self.game
		player = self.player
		
		index = self.location_cbx.current()
		
		location = self.locations[index]
		
		game.create_map(player, location)
		
		game.inc_time()
		
		root.play_screen.update_screen()
		
		self.destroy()
		
class ReadMapPopup(Popup):
	def __init__(self, root, map_obj):
		super().__init__(root)
		
		self.map_obj = map_obj
		
		name_lbl = ttk.Label(self, text=f"Location Name: {map_obj.location_name}", anchor="center")
		name_lbl.pack()
		
		type_lbl = ttk.Label(self, text=f"Location Type: {map_obj.location_type}", anchor="center")
		type_lbl.pack()
		
		coors_lbl = ttk.Label(self, text=f"Coordinates: ({map_obj.x},{map_obj.y})", anchor="center")
		coors_lbl.pack()
		
		cartographer_lbl = ttk.Label(self, text=f"Cartographer: {map_obj.cartographer_name}", anchor="center")
		cartographer_lbl.pack()
		
		ok_btn = ttk.Button(self, text="OK", command=self.destroy)
		ok_btn.pack()
		
		self.center()
		
class ShopPopup(Popup):
	def __init__(self, root, location):
		super().__init__(root)
		
		self.root = root
		self.game = game = root.game
		self.player = player = game.player
		
		location_lbl = ttk.Label(self, text=location.name, anchor="center")
		location_lbl.pack(fill=X)
		
		self.gold_var = StringVar(value=f"Gold: {player.gold}")
		
		gold_lbl = ttk.Label(self, textvariable=self.gold_var, anchor="center")
		gold_lbl.pack(fill=X)
		
		self.shop_nb = ShopNotebook(self, root, location)
		self.shop_nb.pack(fill=BOTH, expand=1)
		
		ok_btn = ttk.Button(self, text="OK", command=self.destroy)
		ok_btn.pack(fill=X)
		
		self.center()
		
	def update_popup(self):
		self.gold_var.set(f"Gold: {self.player.gold}")
		
class ShopNotebook(ttk.Notebook):
	def __init__(self, parent, root, location):
		super().__init__(parent)
		
		self.parent = parent
		self.root = root
		self.location = location
		
		self.tabs = {
			"Buy": BuyTab(self),
			"Sell": SellTab(self),
		}
		
		for tab_name, tab in self.tabs.items():
			self.add(tab, text=tab_name)
			
	def update_tabs(self):
		self.parent.update_popup()
		
		for tab in self.tabs.values():
			try:
				tab.update_tab()
			
			except AttributeError:
				pass
		
class BuyTab(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.shop_nb = parent
		self.location = parent.location
		self.root = parent.root
		self.game = self.root.game
		self.player = self.game.player
		
		self.grid = MapTradeGrid(self, self.location.maps)
		self.grid.pack(fill=BOTH, expand=1)
		
		buy_btn = ttk.Button(self, text="Buy Map", command=self.buy_map)
		buy_btn.pack(fill=X)
		
	def buy_map(self):
		map_obj = self.grid.get_selected_map()
		
		if map_obj is None:
			return
			
		success = self.game.buy_map(self.player, self.location, map_obj)
		
		if success:
			self.root.play_screen.update_screen()
			self.shop_nb.update_tabs()
		
	def update_tab(self):
		self.grid.populate_maps()
		
class SellTab(ttk.Frame):	
	def __init__(self, parent):
		super().__init__(parent)
		
		self.shop_nb = parent
		self.location = parent.location
		self.root = parent.root
		self.game = self.root.game
		self.player = self.game.player
		
		self.grid = MapTradeGrid(self, self.player.maps)
		self.grid.pack(fill=BOTH, expand=1)
		
		sell_btn = ttk.Button(self, text="Sell Map", command=self.sell_map)
		sell_btn.pack(fill=X)
		
	def sell_map(self):
		map_obj = self.grid.get_selected_map()
		
		if map_obj is None:
			return
			
		success = self.game.sell_map(self.player, self.location, map_obj)
		
		if success:
			self.root.play_screen.update_screen()
			self.shop_nb.update_tabs()
			
	def update_tab(self):
		self.grid.populate_maps()
		
class MapTradeGrid(ttk.Treeview):
	def __init__(self, parent, maps):
		columns = ("name", "type", "cartographer", "price")
		
		super().__init__(parent, columns=columns, show="headings")
		
		self.maps = maps
		
		self.heading("name", text="Name")
		self.heading("type", text="Type")
		self.heading("cartographer", text="Cartographer")
		self.heading("price", text="Price")
		
		for col in columns:
			self.column(col, width=120, anchor="center", stretch=True)
			
		self.populate_maps()
		
	def populate_maps(self):
		for row in self.get_children():
			self.delete(row)
			
		for index, map_obj in enumerate(self.maps):
			self.insert(
				"",
				"end",
				iid=str(index),
				values=(
					map_obj.location_name,
					map_obj.location_type,
					map_obj.cartographer_name,
					map_obj.price,
				)
			)
			
	def get_selected_map(self):
		selected = self.selection()
		
		if not selected:
			return None
			
		index = int(selected[0])
		
		return self.maps[index]
		
class StatusFrame(ttk.Frame):
	def __init__(self, parent, root, game):
		super().__init__(parent)
		
		self.root = root
		self.game = game	
		self.player = player = game.player
		
		self.gold_var = StringVar(value=f"Gold: {player.gold}")
		
		gold_lbl = ttk.Label(self, textvariable=self.gold_var, anchor="center")
		gold_lbl.pack(fill=X)
		
		self.status_nb = StatusNotebook(self, root, game)
		self.status_nb.pack(fill=BOTH, expand=1)
		
	def update_frame(self):
		self.gold_var.set(f"Gold: {self.player.gold}")
		
		self.status_nb.update_tabs()
		
class StatusNotebook(ttk.Notebook):
	def __init__(self, parent, root, game):
		super().__init__(parent)
		
		self.root = root
		
		self.game = game
		
		self.tabs = {
			"Cartography": CartographyTab(self, root, game),
			"Locations": LocationsTab(self, root, game),
			"Maps": MapsTab(self, root, game),
		}
		
		for tab_name, tab in self.tabs.items():
			self.add(tab, text=tab_name)
			
	def update_tabs(self):
		for tab in self.tabs.values():
			tab.update_tab()
		
class LocationsTab(ttk.Frame):
	def __init__(self, parent, root, game):
		super().__init__(parent)
		
		self.root = root
		self.game = game
		self.player = game.player
		
		self.discovery_var = StringVar()
		
		discovery_lbl = ttk.Label(self, textvariable=self.discovery_var, anchor="center")
		discovery_lbl.pack(fill=X)
		
		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=1)
		
		self.update_locations()
		
	def update_tab(self):
		self.update_locations()
		
	def update_locations(self):
		discovered = len(self.player.known_locations)
		
		total = len(self.game.locations)
		
		self.discovery_var.set(f"{discovered}/{total} Locations Discovered")
		
		for widget in self.scrollable_fr.scrolling_frame.winfo_children():
			widget.destroy()
			
		locations = sorted(self.player.known_locations.values(), key=lambda location: location.name)
		
		for location in locations:
			lbl = ttk.Label(self.scrollable_fr.scrolling_frame, text=f"{location.name} ({location.location_type}) ({location.x}, {location.y})", anchor="center")
			lbl.pack(fill=X)
			
class CartographyTab(ttk.Frame):
	def __init__(self, parent, root, game):
		super().__init__(parent)
		
		self.root = root
		self.game = game
		self.player = player = game.player
		
		self.cartography_var = StringVar(value=f"Cartography Level: {player.cartography_lvl}")
		
		cartography_lbl = ttk.Label(self, textvariable=self.cartography_var, anchor="center")
		cartography_lbl.pack(fill=X)
		
		self.cartography_xp_var = StringVar(value=f"Cartography XP: {self.player.cartography_xp} / {(self.player.cartography_xp + 1) * 100}")
		
		cartography_xp_lbl = ttk.Label(self, textvariable=self.cartography_xp_var, anchor="center")
		cartography_xp_lbl.pack(fill=X)
		
		self.create_map_btn = ttk.Button(self, text="Create Map", command=lambda:CreateMapPopup(root))
		self.create_map_btn.pack(pady=10)
		
	def update_tab(self):
		self.cartography_var.set(f"Cartography Level: {self.player.cartography_lvl}")
		self.cartography_xp_var.set(f"Cartography XP: {self.player.cartography_xp} / {(self.player.cartography_xp + 1) * 100}")
class MapsTab(ttk.Frame):
	def __init__(self, parent, root, game):
		super().__init__(parent)
		
		self.root = root
		self.game = game
		self.player = player = game.player
		
		self.scrollable_fr = ScrollableFrame(self)
		self.scrollable_fr.pack(fill=BOTH, expand=1)
		
	def update_tab(self):
		self.update_maps()
		
	def update_maps(self):
		for widget in self.scrollable_fr.scrolling_frame.winfo_children():
			widget.destroy()
			
		for map_item in self.player.maps:
			map_fr = MapFrame(self.scrollable_fr.scrolling_frame, self.root, map_item)
			map_fr.pack(fill=X)
			
class MapFrame(ttk.Frame):
	def __init__(self, parent, root, map_obj):
		super().__init__(parent)
		
		self.root = root
		self.game = game = root.game
		
		lbl = ttk.Label(self, text=f"{map_obj.location_name} ({map_obj.location_type})", anchor="center")
		lbl.pack(side=LEFT, fill=X, expand=1)
		
		self.read_btn = ttk.Button(self, text="Read", command=lambda:ReadMapPopup(root, map_obj))
		self.read_btn.pack(side=RIGHT)
		
		
class ScrollableFrame(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)

		# Create & Display Canvas/Scrollbar
		self.canvas = Canvas(self)
		self.canvas.pack(side=LEFT, fill=BOTH, expand=1)

		self.scrollbar = ttk.Scrollbar(
			self,
			orient="vertical",
			command=self.canvas.yview,
		)
		self.scrollbar.pack(side=RIGHT, fill=Y)

		self.scrolling_frame = ttk.Frame(self.canvas)

		# Connect Canvas and Scrollbar
		self.canvas.configure(
			yscrollcommand=self.scrollbar.set
		)

		# Add Scrolling Frame to Canvas
		self.canvas_window = self.canvas.create_window(
			(0, 0),
			window=self.scrolling_frame,
			anchor="nw",
		)

		self.scrolling_frame.bind(
			"<Configure>",
			self.update_scrollregion,
		)

		self.canvas.bind(
			"<Configure>",
			self.resize_frame,
		)

	def update_scrollregion(self, event=None):
		# Update Scrollregion when Scrolling Frame size changes
		self.canvas.configure(
			scrollregion=self.canvas.bbox("all")
		)

	def resize_frame(self, event=None):
		# Makes Scrolling Frame match Canvas width
		canvas_width = event.width

		self.canvas.itemconfigure(
			self.canvas_window,
			width=canvas_width,
		)

class Game:
	def __init__(self):
		self.world_size = 300
		
		self.calendar = CQCalendar()
		
		self.location_num = max(1, int(self.world_size * .30))
		
		self.locations = {}
		
		self.location_types = [
			"Town",
			"Village",
			"Cave",
			"Dungeon",
			"Ruins",
		]
		
		self.location_prefixes = [
			"Oak",
			"River",
			"Stone",
			"Iron",
			"Gold",
			"Black",
			"White",
			"Green",
			"Red",
			"Wolf",
			"Dragon",
			"Ash",
			"Silver",
			"Bright",
			"Dark",
			"Raven",
			"Pine",
			"Storm",
			"Moon",
			"Sun",
		]
		
		self.location_suffixes = [
			"dale",
			"ford",
			"wood",
			"field",
			"brook",
			"haven",
			"keep",
			"port",
			"crest",
			"hold",
			"shire",
			"vale",
			"hill",
			"watch",
			"gate",
			"moor",
			"stone",
			"fall",
			"reach",
			"bury",
		]
		
		self.player = player = Player()
		self.random_character_placement(player)
		
		self.cartographer_num = max(1, int(self.world_size * .1))
		
		self.cartographers = []
		
		self.first_names = [
			"Alden",
			"Aric",
			"Borin",
			"Cedric",
			"Darian",
			"Edric",
			"Eldon",
			"Finn",
			"Gareth",
			"Hadrian",
			"Joran",
			"Kael",
			"Lukas",
			"Marcus",
			"Nolan",
			"Orin",
			"Perrin",
			"Roland",
			"Tobias",
			"Victor",
			"Willow",
			"Elara",
			"Lyra",
			"Selene",
			"Mira",
			"Aria",
			"Fiona",
			"Raven",
			"Sylvia",
			"Talia",
		]
		
		self.last_names = [
			"Ashford",
			"Blackwood",
			"Brightwater",
			"Dawncrest",
			"Emberfall",
			"Fairfield",
			"Goldbrook",
			"Graystone",
			"Greenfield",
			"Hawthorne",
			"Ironwood",
			"Lightfoot",
			"Moonbrook",
			"Oakheart",
			"Ravenwood",
			"Riverstone",
			"Silverbrook",
			"Stonehill",
			"Stormwatch",
			"Thornfield",
			"Valewood",
			"Westbrook",
			"Whitehall",
			"Wildmere",
			"Winterborn",
			"Wolfbane",
			"Woodhaven",
			"Wyrmwood",
			"Youngblood",
			"Redfield",
		]
		
		self.characters = [self.player]
		
		self.generate_locations()
		
		self.generate_cartographers()
		
		self.generate_shop_maps()
		
		self.discover_nearby_locations(self.player)
		
	def random_character_placement(self, character):
		character.x = random.randint(0, self.world_size - 1)
		character.y = random.randint(0, self.world_size - 1)
		
	def generate_locations(self):
		for i in range(self.location_num):
			x = random.randint(0, self.world_size - 1)
			y = random.randint(0, self.world_size - 1)
			
			if (x, y) in self.locations:
				continue
				
			location_type = random.choice(self.location_types)
			
			prefix = random.choice(self.location_prefixes)
			suffix = random.choice(self.location_suffixes)
			name = f"{prefix}{suffix}"
			
			location = Location(
				name,
				location_type,
				x,
				y,
			)
			
			self.locations[(x, y)] = location
			
	def discover_nearby_locations(self, character):
		new_locations = []
		
		for y in range(character.y - 1, character.y + 2):
			for x in range(character.x - 1, character.x + 2):
				location = self.locations.get((x, y))
				
				if location is not None and (x, y) not in character.known_locations:
					character.known_locations[(x, y)] = location
					new_locations.append(location)
					
		return new_locations
					
	def update_characters(self):
		discovered_locations = []
		
		for character in self.characters:
			new_locations = self.discover_nearby_locations(character)
			
			if character is self.player:
				discovered_locations.extend(new_locations)
				
		return discovered_locations
		
	def generate_cartographers(self):
		for i in range(self.cartographer_num):
			first = random.choice(self.first_names)
			last = random.choice(self.last_names)
			
			name = f"{first} {last}"
			
			cartographer = NPC(name)
			
			self.random_character_placement(cartographer)
			
			self.cartographers.append(cartographer)
			
			self.characters.append(cartographer)
			
	def create_map(self, character, location):
		x = location.x
		y = location.y
		
		skill_check = character.cartography_skill_check()
		
		if not skill_check:
			x = random.randint(0, self.world_size - 1)
			y = random.randint(0, self.world_size - 1)
			
		map = Map(
			location.name,
			location.location_type,
			x,
			y,
			character.name,
			price = character.cartography_lvl
		)
		
		character.maps.append(map)
		
		character.gain_cartography_xp()
		
	def buy_map(self, buyer, settlement, map_obj):
		if buyer.gold < map_obj.price:
			return False
			
		buyer.gold -= map_obj.price
			
		settlement.maps.remove(map_obj)
		buyer.maps.append(map_obj)
		
		return True
		
	def sell_map(self, seller, settlement, map_obj):
		if map_obj not in seller.maps:
			return False
			
		seller.gold += map_obj.price
			
		seller.maps.remove(map_obj)
		
		settlement.maps.append(map_obj)
		
		return True
		
	def generate_shop_maps(self):
		settlements = [
			location for location in self.locations.values() if location.location_type in ["Town", "Village"]
		]
		
		if not settlements:
			return
			
		for cartographer in self.cartographers:
			for i in range(5):
				location = random.choice(list(self.locations.values()))
				settlement = random.choice(settlements)
				
				self.create_map(cartographer, location)
				
				if cartographer.maps:
					map_obj = cartographer.maps[-1]
					
					cartographer.maps.remove(map_obj)
					
					settlement.maps.append(map_obj)
		
	def inc_time(self, ticks=60):
		self.calendar.update(ticks=ticks)
		
class Location:
	def __init__(self, name, location_type, x, y):
		self.name = name
		
		self.location_type = location_type
		
		self.char = location_type[0]
		
		self.x = x
		self.y = y
		
		self.maps = []
		
class Character:
	def __init__(self):
		self.name = "Character"
		
		self.x = 0
		self.y = 0
		
		self.char = '@'
		
		self.known_locations = {}
		
		self.gold = 0
		
		self.cartography_lvl = 1
		
		self.cartography_xp = 0
		
		self.maps = []
		
	def cartography_skill_check(self):
		if random.randint(1, 100) <= self.cartography_lvl:
			return True
			
		else:
			return False
			
	def gain_cartography_xp(self):
		xp_gain = random.randint(1, self.cartography_lvl)
		
		self.cartography_xp += xp_gain
		
		xp_needed = (self.cartography_lvl + 1) * 100
		
		if self.cartography_xp >= xp_needed:
			self.cartography_xp -= xp_needed
			self.cartography_lvl += 1
		
class Player(Character):
	def __init__(self):
		super().__init__()
		
		self.name = "Player"
		
class NPC(Character):
	def __init__(self, name):
		super().__init__()
		
		self.name = name
		
		self.cartography_lvl = random.randint(1, 100)
		
class Map:
	def __init__(self, location_name, location_type, x, y, cartographer_name, price=1):
		self.location_name = location_name
		
		self.location_type = location_type
		
		self.x = x
		self.y = y
		
		self.cartographer_name = cartographer_name
		
		self.price = price
		
if __name__ == "__main__":
	root = Root()
	
	root.mainloop()