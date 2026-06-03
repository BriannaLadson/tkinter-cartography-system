from tkinter import *
from tkinter import ttk
import random

def process_cmd(play_screen, cmd):
	try:
		cmd_dict[cmd](play_screen, cmd)
		
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
		
cmd_dict = {
	"up": move_cmd,
	"northwest": move_cmd,
	"northeast": move_cmd,
	"down": move_cmd,
	"southwest": move_cmd,
	"southeast": move_cmd,
	"left": move_cmd,
	"right": move_cmd,
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
		
		self.player = player = game.player
		
		left_fr = ttk.Frame(self)
		left_fr.pack(side=LEFT, fill=Y)
		
		self.status_fr = StatusFrame(left_fr, root, game)
		self.status_fr.pack(fill=BOTH, expand=1)
		
		right_fr = ttk.Frame(self)
		right_fr.pack(side=LEFT, fill=BOTH, expand=1)
		
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
		
		self.update_screen()
		
	def update_screen(self):
		self.update_location()
		
		self.status_fr.update_frame()
		
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
		
		self.player = root.game.player
		
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
				f"{location.name} ({location.location_type}) {location.x, {location.y}}" for location in self.locations
			]
			
			self.location_cbx = ttk.Combobox(self, textvariable=self.location_var, values=location_names, state="readonly",)
			self.location_cbx.pack(fill=X, padx=10, pady=10)
			
			if location_names:
				self.location_cbx.current(0)
				
			self.create_btn = ttk.Button(self, text="Create Map", command=self.create_map)
			self.create_btn.pack(padx=10, pady=10)
			
		self.center()
		
	def create_map(self):
		self.destroy()
		
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
		self.status_nb.update_tabs()
		
class StatusNotebook(ttk.Notebook):
	def __init__(self, parent, root, game):
		super().__init__(parent)
		
		self.root = root
		
		self.game = game
		
		self.tabs = {
			"Cartography": CartographyTab(self, root, game),
			"Locations": LocationsTab(self, root, game),
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
			lbl = ttk.Label(self.scrollable_fr.scrolling_frame, text=f"{location.name} ({location.location_type}) {location.x}, {location.y}", anchor="center")
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
		
		self.create_map_btn = ttk.Button(self, text="Create Map", command=lambda:CreateMapPopup(root))
		self.create_map_btn.pack(pady=10)
		
	def update_tab(self):
		self.cartography_var.set(f"Cartography Level: {self.player.cartography_lvl}")
		
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
		
class Location:
	def __init__(self, name, location_type, x, y):
		self.name = name
		
		self.location_type = location_type
		
		self.char = location_type[0]
		
		self.x = x
		self.y = y
		
class Character:
	def __init__(self):
		self.x = 0
		self.y = 0
		
		self.char = '@'
		
		self.known_locations = {}
		
		self.gold = 0
		
		self.cartography_lvl = 1
		
class Player(Character):
	def __init__(self):
		super().__init__()
		
class NPC(Character):
	def __init__(self, name):
		super().__init__()
		
		self.name = name
		
		self.cartography_lvl = random.randint(1, 100)
		
class Map:
	def __init__(self, location_name, location_type, x, y, cartographer_name):
		self.location_name = location_name
		
		self.location_type = location_type
		
		self.x = x
		self.y = y
		
		self.cartographer_name = cartographer_name
		
if __name__ == "__main__":
	root = Root()
	
	root.mainloop()