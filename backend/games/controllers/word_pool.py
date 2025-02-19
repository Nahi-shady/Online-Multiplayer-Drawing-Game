EASY_WORDS = [
    "apple", "ball", "cat", "dog", "house", "tree", "sun", "moon", "star", "flower",
    "car", "book", "pen", "hat", "shoe", "fish", "chair", "cup", "bird", "cake",
    "cloud", "rain", "bee", "leaf", "bread", "milk", "box", "bag", "key", "clock",
    "lamp", "phone", "ring", "egg", "boat", "bed", "sock", "glasses", "kite", "bat",
    "banana", "spoon", "fork", "shirt", "pants", "door", "fence", "hand", "face", "nose",
    "ear", "lion", "cow", "goat", "turtle", "duck", "chicken", "horse", "rabbit", "owl",
    "butterfly", "snail", "dolphin", "whale", "pumpkin", "candle", "ice", "balloon", "bell", "drum",
    "piano", "guitar", "peach", "watermelon", "grape", "mango", "strawberry", "cherry", "pineapple", "cupcake",
    "hamburger", "pizza", "donut", "hotdog", "cookie", "pot", "pan", "ladder", "mask", "broom",
    "basket", "map", "coin", "fan", "robot", "window", "paper", "pencil", "marker", "eraser",
    "Jump", "Run", "Swim", "Clap", "Dance","Sing", "Wave", "Sit", "Stand", "Smile", "Walk", "Throw", "Catch", "Push", 
    "Pull", "Kick", "Ride", "Talk", "Drink", "Eat", "Sleep", "Cry", "Laugh", "Hug", "Climb", "Read", "Write", "Point", "Cook", "Shout", 
    "Paint", "Draw", "Build", "Dig", "Play", "Hop", "Crawl", "Shake", "Skate", "Skip", "Open", "Close", "Wash", "Clean", "Fix", "Wave", 
    "Scratch", "Think", "Listen", "Watch", "Run", "Sneeze", "Stretch", "Lift", "Carry", "Fly", "Sit", "Yawn", "Dribble", "Shoot",
    "Jump Rope", "Blow", "Wave", "Comb", "Brush", "Tie", "Wear", "Jump", "Kick", "Spin", "Swing", "Dive", "Cheer", "Run", "Stand", 
    "Shake", "Read", "Smile", "Write", "Wait", "Balance", "Count", "Wave", "Rest", "Look", "Cry", "Crawl", "Stare", "Blink", "Ride", 
    "Turn", "Walk", "Push", "Pull", "Eat", "sponge", "soap", "toothbrush", "toothpaste", "carrot", "onion", "potato", "tomato",
    "cucumber", "pepper", "lettuce", "treehouse", "nest", "snowman", "igloo", "kite", "lollipop", "rocket", "starfish", "surfboard",
    "beach", "sand", "tent", "fire", "lightning", "mountain", "hill", "river", "lake", "bridge",
    "train", "plane", "helicopter", "truck", "bike", "tractor", "bus", "subway", "cab", "owl",
    "squirrel", "penguin", "seal", "kangaroo", "koala", "elephant", "giraffe", "monkey", "bear", "zebra",
    "camel", "crab", "shark", "jellyfish", "ant", "ladybug", "spider", "octopus", "lobster", "peacock",
    "parrot", "canary", "crow", "duckling", "sparrow", "seagull", "owl", "flamingo", "rooster", "hedgehog",
    "hamster", "mouse", "rat", "kitten", "puppy", "wolf", "fox", "panda", "polar bear", "walrus",
    "seal", "otter", "iguana", "snake", "frog", "lizard", "alligator", "crocodile", "tiger", "cheetah",
    "panther", "leopard", "jaguar", "gorilla", "chimpanzee", "orangutan", "dinosaur", "t-rex", "triceratops", "stegosaurus",
    "pterodactyl", "volcano", "lava", "island", "palm tree", "coconut", "shovel", "bucket", "swing", "slide",
    "seesaw", "carousel", "ball pit", "sandbox", "brick", "log", "leaf pile", "feather", "petal", "snowflake",
    "ice cube", "rainbow", "cloud", "sunset", "sunrise", "ocean", "wave", "surfboard", "scarf", "glove",
    "hat", "helmet", "backpack", "watch", "bracelet", "necklace", "earring", "crown", "ring", "trophy",
    "medal", "ribbon", "triangle", "square", "circle", "rectangle", "heart", "diamond", "hexagon", "octagon",
    "parallelogram", "trapezoid", "spiral", "zigzag", "ladder", "fence", "wall", "gate", "path", "road",
    "sidewalk", "driveway", "parking lot", "garage", "doorbell", "mailbox", "porch", "bench", "lamp post", "streetlight",
    "fire hydrant", "stop sign", "traffic light", "crosswalk", "bus stop", "taxi", "scooter", "tractor", "anchor", "parachute",
    "snowball", "campfire", "tent", "frost", "icicle", "windmill", "lighthouse", "barn", "silo", "saddle",
    "cowboy", "lasso", "straw", "haystack", "trampoline", "sled", "sleddog", "hot air balloon", "microscope", "telescope",
    "globe", "flag", "compass", "thermometer", "stethoscope", "test tube", "beaker", "magnifying glass", "clover", "daisy",
    "poppy", "rose", "cactus", "fern", "oak tree", "pine tree", "willow tree", "bonsai tree", "vine", "grapevine",
    "cherry blossom", "sakura", "tulip", "orchid", "sunflower", "poinsettia", "holly", "mistletoe", "acorn", "pinecone",
    "bonsai", "daffodil", "ivy", "bamboo", "dandelion", "mushroom", "fungus", "shell", "pearl", "reef",
    "coral", "seaweed", "kelp", "barnacle", "algae", "driftwood", "buoy", "rowboat", "canoe", "kayak",
    "raft", "sailboat", "yacht", "submarine", "ferry", "gondola", "cruise ship", "speedboat", "jet ski", "motorboat",
    "pirate", "treasure", "gold", "silver", "jewels", "ruby", "emerald", "sapphire", "pearl", "diamond",
    "coin", "dollar", "banknote", "wallet", "piggy bank", "vault", "safe", "check", "credit card", "debit card",
    "receipt", "ticket", "passport", "license", "permit", "contract", "agreement", "signature", "seal", "stamp",
    "ink", "quill", "parchment", "scroll", "manuscript", "book", "notebook", "diary", "journal", "album",
    "photograph", "camera", "lens", "tripod", "flash", "battery", "plug", "outlet", "wire", "cable",
    "cord", "rope", "string", "twine", "thread", "needle", "scissors", "knife", "saw", "hammer",
    "nail", "screw", "wrench", "pliers", "drill", "toolbox", "workbench", "ladder", "step stool", "shelf",
    "cabinet", "drawer", "closet", "hanger", "rod", "pole", "flagpole", "lamp", "chandelier", "lantern",
    "torch", "candle", "flashlight", "light bulb", "spotlight", "laser", "projector", "mirror", "window", "shutter",
    "curtain", "blind", "shade", "awning", "umbrella", "parasol", "canopy", "tent", "tarpaulin", "mat",
    "rug", "carpet", "floor", "tile", "brick", "stone", "pebble", "boulder", "rock", "cliff",
    "mountain", "hill", "valley", "canyon", "gorge", "plateau", "mesa", "volcano", "lava", "ash",
    "smoke", "steam", "fog", "mist", "rain", "snow", "hail", "sleet", "drizzle", "shower",
    "thunder", "lightning", "storm", "cyclone", "hurricane", "typhoon", "tornado", "earthquake", "tsunami", "flood",
    "drought", "heatwave", "blizzard", "avalanche", "wildfire", "forest", "woods", "jungle", "rainforest", "desert",
    "savannah", "prairie", "grassland", "steppe", "taiga", "tundra", "arctic", "antarctica", "ocean", "sea",
    "lake", "pond", "river", "stream", "creek", "brook", "waterfall", "spring", "geyser", "fountain",
    "well", "aqueduct", "reservoir", "dam", "canal", "bridge", "tunnel", "viaduct", "overpass", "underpass",
    "intersection", "crossroad", "roundabout", "highway", "freeway", "expressway", "road", "street", "avenue", "boulevard",
    "lane", "alley", "path", "trail", "walkway", "sidewalk", "driveway", "parking lot", "garage", "carport",
    "shed", "barn", "stable", "coop", "pen", "corral", "paddock", "arena", "stadium", "court",
    "field", "track", "rink", "pool", "lake", "ocean", "beach", "shore", "coast", "island"
]


HARD_WORDS = [
    "alligator", "ambulance", "amusement", "ankle", "antenna", "applause", "aquarium", "archery", 
    "avocado", "backpack", "ballet", "bamboo", "banjo", "barnacle", "beaver", "bedtime", "biscuit", 
    "blacksmith", "blueprint", "boomerang", "boulder", "bowtie", "bubble", "bulldozer", "butterfly", 
    "cactus", "campfire", "candle", "carnival", "catapult", "centipede", "chainsaw", "chandelier", 
    "cheetah", "chimney", "chisel", "cliffhanger", "cloudburst", "coconut", "compass", "cricket", 
    "crossbow", "cyclone", "dandelion", "dinosaur", "dolphin", "dragonfly", "earmuffs", "easel", 
    "eggplant", "electricity", "elephant", "escalator", "fiddle", "fireplace", "firetruck", "fishing", 
    "flamingo", "floodlight", "fountain", "galaxy", "garden", "glacier", "globe", "goldfish", 
    "grandfather", "greenhouse", "grizzly", "guitar", "hamburger", "hammock", "headphones", "helicopter", 
    "honeycomb", "hotdog", "iceberg", "igloo", "jellyfish", "jigsaw", "kangaroo", "kitchen", 
    "kiwi", "koala", "lantern", "lava", "lawnmower", "lightbulb", "lighthouse", "limousine", 
    "locust", "mailbox", "meadow", "mermaid", "microscope", "monarch", "motorcycle", "mushroom", 
    "narwhal", "necklace", "nightfall", "octopus", "orca", "ostrich", "parachute", "parrot", 
    "peacock", "penguin", "pepper", "phoenix", "picnic", "piano", "pineapple", "pogo stick", 
    "puzzle", "quicksand", "raincoat", "rainforest", "reindeer", "rhino", "ringmaster", "robot", 
    "rollercoaster", "safari", "saxophone", "scarecrow", "scooter", "seahorse", "shamrock", "shark", 
    "skateboard", "skyscraper", "snowman", "spaceship", "spaghetti", "spectacles", "speedboat", "spiderweb", 
    "spiral", "springboard", "squirrel", "staircase", "stargazer", "stethoscope", "storm", "submarine", 
    "sundial", "sunglasses", "surfboard", "swing", "tarantula", "teapot", "tepee", "thermometer", 
    "thunderstorm", "toothbrush", "tornado", "toucan", "tractor", "traffic", "treasure", "tricycle", 
    "trumpet", "tugboat", "turquoise", "turtle", "umbrella", "unicorn", "vampire", "volcano", 
    "waterfall", "wheelbarrow", "windmill", "witch", "woodpecker", "xylophone", "yacht", "zebra",
    "accordion", "acorn", "alpaca", "anchor", "anteater", "arrowhead", "artichoke", "asteroid", 
    "balloon", "banana split", "barnyard", "biplane", "blender", "bonsai", "bouncy castle", "brontosaurus", 
    "bubble wrap", "butterscotch", "cabbage", "camel", "canoe", "carousel", "cash register", "castle", 
    "catfish", "chameleon", "cheeseburger", "cherry blossom", "chimney sweep", "chocolate bar", "chrysanthemum", 
    "clownfish", "cobblestone", "coconut tree", "cornfield", "cotton candy", "crayfish", "crescent moon", 
    "crow's nest", "crystal ball", "cuckoo clock", "daisy chain", "dandelion fluff", "dreamcatcher", "duckling", 
    "fairy tale", "feather boa", "ferris wheel", "fire hydrant", "firecracker", "fireworks", "foxglove", 
    "frostbite", "giraffe", "golden retriever", "golden snitch", "gooseberry", "harp", "hermit crab", 
    "hot air balloon", "hoverboard", "iguana", "inchworm", "jack-in-the-box", "jet ski", "jukebox", 
    "jungle gym", "kaleidoscope", "kazoo", "lava lamp", "leprechaun", "light saber", "limbo stick", 
    "lobster", "magic carpet", "marshmallow", "milkshake", "moth", "mountain goat", "movie projector", 
    "mustache", "nightlight", "obelisk", "ostrich egg", "paddleboat", "paintbrush", "paper airplane", 
    "parasol", "peanut butter", "pepperoni pizza", "petunia", "platypus", "popcorn machine", "porcupine", 
    "postcard", "quilt", "quokka", "rocking chair", "rocket ship", "rose bush", "rubber duck", 
    "saddle", "seashell", "sequoia", "shamrock", "skeleton key", "slingshot", "snowflake", "space helmet", 
    "sparkler", "starfish", "strawberry shortcake", "sundae", "swing set", "tambourine", "tentacle", 
    "thermos", "thorn bush", "toaster", "trellis", "truffle", "tsunami", "umbrella stand", "unicycle", 
    "vacuum cleaner", "vending machine", "violin bow", "watermelon slice", "weather vane", "whale shark", 
    "wind chime", "woodland", "zeppelin", "zigzag",
    "Whistle", "Jog", "Meditate", "Box", "Frown", 
    "Juggle", "Faint", "Spin", "Sketch", "Argue", 
    "Chop", "Ski", "Fish", "Clap", "Row", 
    "Snore", "Swirl", "Cheer", "Stack", "Fold", 
    "Dribble", "Swing", "Tumble", "March", "Tackle", 
    "Jumping Jacks", "Paddle", "Flip", "Squeeze", "Balance", 
    "Stir", "Measure", "Dig", "Carve", "Grind", 
    "Pray", "Race", "Twist", "Jog", "Strike", 
    "Hunt", "Pose", "Shovel", "Sculpt", "Paint", 
    "Catch", "Serve", "Chip", "Score", "Stretch", 
    "Snorkel", "Surf", "Trim", "Drum", "Tune", 
    "Photograph", "Bounce", "Hurdle", "Tug", "Whittle", 
    "Gaze", "Mow", "Saw", "Type", "Forge", 
    "Gallop", "Swirl", "Grate", "Waltz", "Juggle", 
    "Sharpen", "Kneel", "Wrap", "Mend", "Row", 
    "Swing", "Carve", "Pick", "Toast", "Cleanse", 
    "Harvest", "Quilt", "Mop", "Sweep", "Plant", 
    "Sew", "Nail", "Dust", "Pluck", "Pour"
]

FUN = [
    "Einstein", "Cleopatra", "Napoleon", "Marilyn", "Beyoncé",
    "Picasso", "Obama", "Frida", "Elvis", "Drake", "Kobe",
    "Messi", "Ronaldo", "LeBron", "Adele", "Oprah", "Shaq", 
    "Serena", "Bolt", "Phelps", "Barbie", "Yoda", "Mario",
    "Titanic", "Colosseum", "Pyramids", "Eiffel", "Liberty", 
    "Renaissance", "Mount Rushmore", "Moon", "Stonehenge", "Berlin",
    "Slam Dunk", "Penalty", "Kickoff", "Half-Court", "World Cup", 
    "NBA", "Olympics", "Trophy", "Goalkeeper", "Mascot", 
    "Stadium", "Referee", "Huddle", "Pitcher", "Coach", 
    "Fastball", "Buzzer", "Dribble", "Corner", "Basket",
    "Meme", "TikTok", "SpongeBob", "Shrek", "Grumpy", 
    "Baby Shark", "Emoji", "Reddit", "Twitter", "Netflix", 
    "Avatar", "Minions", "Rickroll", "Dogecoin", "Instagram",
    "Harry Potter", "Avengers", "Homer", "Iron Man", "Batman", 
    "Simpsons", "Darth Vader", "Sherlock", "Elsa", "Frodo", 
    "Gandalf", "Wolverine", "Hulk", "Spiderman", "Buzz Lightyear",
    "Times Square", "Taj Mahal", "Grand Canyon", "Niagara", "Hollywood", 
    "Santorini", "Amazon", "Everest", "Vegas", "Safari", 
    "Venice", "Tokyo", "Santorini", "Rome", "Kyoto",
    "Rubik's Cube", "Pac-Man", "Tetris", "Lego", "Emoji", 
    "Rock Band", "Grammy", "Spaceship", "Robot", "Satellite", 
    "Violin", "Guitar", "DJ", "Vinyl", "Karaoke",
    "Unicorn", "Dragon", "Phoenix", "Mermaid", "Narwhal", 
    "Panda", "Koala", "Giraffe", "Octopus", "Dolphin", 
    "Whale", "Tiger", "Elephant", "Lion", "Kangaroo",
    "Pizza", "Taco", "Sushi", "Donut", "Ice Cream", 
    "Popcorn", "Pancakes", "Hamburger", "French Fries", "Milkshake",
    "Campfire", "Rainbow", "Fireworks", "Ferris Wheel", "Rollercoaster", 
    "Beach Ball", "Volcano", "Sunset", "Jungle", "Safari", 
    "Parachute", "Hot Air Balloon", "Treasure", "Map", "Compass", 
    "Lantern", "Canoe", "Backpack", "Tent", "Surfboard",
    "Moonwalk", "Dab", "Twerk", "Backflip", "High Five", 
    "Selfie", "Shuffle", "Meditate", "Hula Hoop", "Bench Press", 
    "Breakdance", "Karate Kick", "Thumb War", "Juggle", "Thumbs Up", 
    "Yoga", "Mosh", "Skydive", "Bowling", "Arm Wrestle", 
    "Rowing", "Fencing", "Pole Vault", "Boxing", "Push-Up", 
    "Stargaze", "Wink", "Play Guitar", "Tightrope", "Sprint", 
    "Kickbox", "Wrestle", "Parkour", "Hang Gliding", "Flossing", 
    "Snowboard", "Paragliding", "Scuba Dive", "Skateboard", "Sign Language", 
    "Air Guitar", "Bungee Jump", "Catwalk", "Fire Dance", "Sword Fight", 
    "Archery", "Belly Dance", "Mime", "Scarecrow", "Hoverboard", 
    "Catch Fish", "Ride Camel", "Climb Everest", "Treasure Hunt", "Ping Pong", 
    "Canoeing", "Rock Climb", "Shave", "Tattoo", "Shuffle Cards", 
    "Blow Candles", "Target Practice", "Knitting", "Swordplay", "Fishing", 
    "Lasso", "Sailing", "Whistling", "Tightrope Walk", "Skipping Rope", 
    "Duck Walk", "Jump Rope", "Unicycle", "Sculpting", "Javelin", 
    "Flip Pancake", "Blow Bubbles", "Magic Trick", "Zumba", "Planking"
]

