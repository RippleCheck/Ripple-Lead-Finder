"""
categories.py — the business taxonomy.

Each entry maps a friendly category name to:
  tags    : the OpenStreetMap tag pairs that identify it (OR'd together)
  foundry : the matching Ripple Foundry template slug, so a lead can be turned
            straight into a personalised demo link
  seg     : broad segment, used for grouping in the UI

Adding a category is just adding a row here. Nothing else needs to change.
"""

# name: (segment, [ (osm_key, osm_value), ... ], foundry_slug or "")
CATALOGUE = {

    # ── Hospitality & stay ────────────────────────────────────────────────
    "Hotel":                    ("Hospitality", [("tourism", "hotel")], "hotel"),
    "Luxury Hotel / Resort":    ("Hospitality", [("tourism", "resort"), ("leisure", "resort")], "boutique-resort"),
    "Boutique Hotel":           ("Hospitality", [("tourism", "hotel")], "boutique-resort"),
    "Motel":                    ("Hospitality", [("tourism", "motel")], "hotel"),
    "Hostel":                   ("Hospitality", [("tourism", "hostel")], "guest-house"),
    "Guest House / B&B":        ("Hospitality", [("tourism", "guest_house"), ("tourism", "bed_and_breakfast")], "guest-house"),
    "Homestay":                 ("Hospitality", [("tourism", "guest_house")], "guest-house"),
    "Vacation Rental":          ("Hospitality", [("tourism", "chalet"), ("tourism", "apartment")], "bnb"),
    "Serviced Apartments":      ("Hospitality", [("tourism", "apartment")], "bnb"),
    "Camping / Caravan Site":   ("Hospitality", [("tourism", "camp_site"), ("tourism", "caravan_site")], "adventure-tours"),

    # ── Food & beverage ───────────────────────────────────────────────────
    "Restaurant":               ("Food & Drink", [("amenity", "restaurant")], "restaurant"),
    "Fine Dining":              ("Food & Drink", [("amenity", "restaurant")], "fine-dining"),
    "Pizzeria":                 ("Food & Drink", [("cuisine", "pizza"), ("amenity", "fast_food")], "pizzeria"),
    "Sushi / Japanese":         ("Food & Drink", [("cuisine", "sushi"), ("cuisine", "japanese")], "sushi"),
    "Cafe":                     ("Food & Drink", [("amenity", "cafe")], "cafe"),
    "Coffee Shop / Roaster":    ("Food & Drink", [("shop", "coffee")], "coffee-roaster"),
    "Tea House":                ("Food & Drink", [("shop", "tea")], "cafe"),
    "Bakery":                   ("Food & Drink", [("shop", "bakery"), ("shop", "pastry")], "bakery"),
    "Confectionery / Sweets":   ("Food & Drink", [("shop", "confectionery"), ("shop", "chocolate")], "bakery"),
    "Ice Cream Shop":           ("Food & Drink", [("amenity", "ice_cream"), ("shop", "ice_cream")], "juice-bar"),
    "Juice / Smoothie Bar":     ("Food & Drink", [("shop", "beverages")], "juice-bar"),
    "Fast Food":                ("Food & Drink", [("amenity", "fast_food")], "fast-food"),
    "Food Truck":               ("Food & Drink", [("amenity", "fast_food")], "food-truck"),
    "Cloud Kitchen":            ("Food & Drink", [("amenity", "fast_food")], "cloud-kitchen"),
    "Bar":                      ("Food & Drink", [("amenity", "bar")], "bar"),
    "Pub":                      ("Food & Drink", [("amenity", "pub")], "pub"),
    "Lounge":                   ("Food & Drink", [("amenity", "bar")], "lounge"),
    "Nightclub":                ("Food & Drink", [("amenity", "nightclub")], "nightclub"),
    "Brewery":                  ("Food & Drink", [("craft", "brewery"), ("industrial", "brewery")], "brewery"),
    "Winery":                   ("Food & Drink", [("craft", "winery"), ("shop", "wine")], "brewery"),
    "Wine / Liquor Shop":       ("Food & Drink", [("shop", "wine"), ("shop", "alcohol")], "grocery-store"),
    "Catering Service":         ("Food & Drink", [("craft", "caterer")], "catering"),
    "Deli / Fine Food":         ("Food & Drink", [("shop", "deli")], "organic-store"),
    "Butcher":                  ("Food & Drink", [("shop", "butcher")], "grocery-store"),
    "Fishmonger":               ("Food & Drink", [("shop", "seafood")], "grocery-store"),
    "Greengrocer":              ("Food & Drink", [("shop", "greengrocer")], "organic-store"),
    "Health Food Shop":         ("Food & Drink", [("shop", "health_food")], "organic-store"),
    "Farm Shop":                ("Food & Drink", [("shop", "farm")], "organic-store"),

    # ── Healthcare ────────────────────────────────────────────────────────
    "Hospital":                 ("Healthcare", [("amenity", "hospital")], "hospital"),
    "Eye Hospital":             ("Healthcare", [("healthcare:speciality", "ophthalmology")], "eye-hospital"),
    "Medical Clinic":           ("Healthcare", [("amenity", "clinic"), ("amenity", "doctors")], "medical-clinic"),
    "Doctor / GP":              ("Healthcare", [("amenity", "doctors"), ("healthcare", "doctor")], "medical-clinic"),
    "Dentist":                  ("Healthcare", [("amenity", "dentist"), ("healthcare", "dentist")], "dentist"),
    "Dental Clinic":            ("Healthcare", [("amenity", "dentist")], "dental-clinic"),
    "Orthodontist":             ("Healthcare", [("healthcare:speciality", "orthodontics")], "orthodontist"),
    "Dermatology Clinic":       ("Healthcare", [("healthcare:speciality", "dermatology")], "dermatology"),
    "Cosmetic Clinic":          ("Healthcare", [("healthcare", "cosmetic_surgery"), ("shop", "beauty")], "cosmetic-clinic"),
    "Plastic Surgeon":          ("Healthcare", [("healthcare:speciality", "plastic_surgery")], "plastic-surgeon"),
    "Physiotherapy":            ("Healthcare", [("healthcare", "physiotherapist")], "physiotherapy"),
    "Chiropractor":             ("Healthcare", [("healthcare", "chiropractor")], "chiropractic"),
    "Optometrist / Optician":   ("Healthcare", [("shop", "optician"), ("healthcare", "optometrist")], "optometrist"),
    "Diagnostic Lab":           ("Healthcare", [("healthcare", "laboratory")], "diagnostic-lab"),
    "Pharmacy":                 ("Healthcare", [("amenity", "pharmacy"), ("healthcare", "pharmacy")], "pharmacy"),
    "Mental Health Clinic":     ("Healthcare", [("healthcare", "psychotherapist"), ("healthcare:speciality", "psychiatry")], "mental-health"),
    "Fertility / IVF Centre":   ("Healthcare", [("healthcare:speciality", "fertility")], "ivf-centre"),
    "Home Care":                ("Healthcare", [("healthcare", "nurse"), ("social_facility", "nursing_home")], "home-care"),
    "Veterinary Clinic":        ("Healthcare", [("amenity", "veterinary")], "veterinary"),

    # ── Fitness & wellness ────────────────────────────────────────────────
    "Gym / Fitness":            ("Fitness", [("leisure", "fitness_centre")], "gym"),
    "CrossFit Box":             ("Fitness", [("leisure", "fitness_centre")], "crossfit"),
    "Yoga Studio":              ("Fitness", [("leisure", "fitness_centre"), ("sport", "yoga")], "yoga"),
    "Pilates Studio":           ("Fitness", [("sport", "pilates")], "pilates"),
    "Personal Trainer":         ("Fitness", [("leisure", "fitness_centre")], "personal-trainer"),
    "Martial Arts":             ("Fitness", [("sport", "martial_arts"), ("sport", "karate")], "martial-arts"),
    "Swim School":              ("Fitness", [("leisure", "swimming_pool"), ("sport", "swimming")], "swim-school"),
    "Sports Academy":           ("Fitness", [("leisure", "sports_centre")], "sports-academy"),
    "Cricket Academy":          ("Fitness", [("sport", "cricket")], "cricket-academy"),
    "Football Academy":         ("Fitness", [("sport", "soccer"), ("sport", "football")], "football-academy"),
    "Badminton / Court Booking":("Fitness", [("sport", "badminton"), ("leisure", "sports_centre")], "badminton-court"),
    "Spa":                      ("Fitness", [("leisure", "spa"), ("shop", "spa")], "spa"),
    "Massage Center":           ("Fitness", [("shop", "massage")], "massage"),
    "Med Spa":                  ("Fitness", [("shop", "beauty")], "med-spa"),
    "Beauty Salon":             ("Fitness", [("shop", "beauty")], "beauty-salon"),
    "Nail Salon":               ("Fitness", [("shop", "nails"), ("shop", "beauty")], "nail-salon"),
    "Lash & Brow Studio":       ("Fitness", [("shop", "beauty")], "lash-brow"),
    "Barber Shop":              ("Fitness", [("shop", "hairdresser")], "barber"),
    "Hair Salon":               ("Fitness", [("shop", "hairdresser")], "beauty-salon"),
    "Tattoo Studio":            ("Fitness", [("shop", "tattoo")], "tattoo"),
    "Makeup Artist":            ("Fitness", [("shop", "beauty"), ("craft", "beautician")], "makeup-artist"),

    # ── Education ─────────────────────────────────────────────────────────
    "School":                   ("Education", [("amenity", "school")], "school"),
    "College / University":     ("Education", [("amenity", "college"), ("amenity", "university")], "university"),
    "Coaching Institute":       ("Education", [("amenity", "prep_school"), ("office", "educational_institution")], "coaching-institute"),
    "Tuition / Tutoring":       ("Education", [("office", "tutoring")], "tutoring"),
    "Skill Institute":          ("Education", [("amenity", "training")], "skill-institute"),
    "Coding Bootcamp":          ("Education", [("amenity", "training")], "coding-bootcamp"),
    "Music School":             ("Education", [("amenity", "music_school")], "music-school"),
    "Dance Academy":            ("Education", [("leisure", "dance"), ("amenity", "dancing_school")], "dance-studio"),
    "Language Institute":       ("Education", [("amenity", "language_school")], "language-school"),
    "Driving School":           ("Education", [("amenity", "driving_school")], "driving-school"),
    "Childcare / Nursery":      ("Education", [("amenity", "childcare"), ("amenity", "kindergarten")], "child-care"),
    "Library":                  ("Education", [("amenity", "library")], "school"),

    # ── Legal & finance ───────────────────────────────────────────────────
    "Law Firm":                 ("Legal & Finance", [("office", "lawyer")], "law-firm"),
    "Personal Injury Lawyer":   ("Legal & Finance", [("office", "lawyer")], "personal-injury"),
    "Immigration Lawyer":       ("Legal & Finance", [("office", "lawyer")], "immigration-law"),
    "Notary":                   ("Legal & Finance", [("office", "notary")], "law-firm"),
    "Tax Consultant":           ("Legal & Finance", [("office", "tax_advisor")], "tax-consultant"),
    "Accountant":               ("Legal & Finance", [("office", "accountant")], "accounting"),
    "Bookkeeping":              ("Legal & Finance", [("office", "accountant")], "bookkeeping"),
    "Financial Advisor":        ("Legal & Finance", [("office", "financial_advisor"), ("office", "financial")], "financial-advisor"),
    "Wealth Management":        ("Legal & Finance", [("office", "financial")], "wealth-management"),
    "Insurance Agency":         ("Legal & Finance", [("office", "insurance")], "insurance"),
    "Mortgage Broker":          ("Legal & Finance", [("office", "mortgage_broker")], "mortgage-broker"),
    "Loan Agency":              ("Legal & Finance", [("office", "financial")], "loan-agency"),
    "Stock Broker":             ("Legal & Finance", [("office", "financial")], "stock-broker"),
    "Bank / Credit Union":      ("Legal & Finance", [("amenity", "bank")], "financial-advisor"),
    "Company Secretary":        ("Legal & Finance", [("office", "company")], "company-secretary"),

    # ── Property & construction ───────────────────────────────────────────
    "Real Estate Agency":       ("Property", [("office", "estate_agent")], "real-estate"),
    "Property Management":      ("Property", [("office", "property_management")], "property-management"),
    "Property Developer":       ("Property", [("office", "construction_company")], "builder-developer"),
    "Construction Company":     ("Property", [("office", "construction_company"), ("craft", "builder")], "construction"),
    "Civil Contractor":         ("Property", [("craft", "builder")], "civil-contractor"),
    "Home Builder":             ("Property", [("craft", "builder")], "builder-developer"),
    "Renovation":               ("Property", [("craft", "builder"), ("shop", "doityourself")], "renovation"),
    "Interior Designer":        ("Property", [("shop", "interior_decoration"), ("office", "interior_design")], "interior-design"),
    "Architect":                ("Property", [("office", "architect")], "architecture"),
    "Landscape Architect":      ("Property", [("office", "architect"), ("craft", "gardener")], "landscape-architect"),
    "Surveyor":                 ("Property", [("office", "surveyor")], "architecture"),
    "Self Storage":             ("Property", [("shop", "storage_rental")], "self-storage"),
    "Coworking Space":          ("Property", [("office", "coworking"), ("amenity", "coworking_space")], "coworking-space"),

    # ── Retail & fashion ──────────────────────────────────────────────────
    "Clothing Store":           ("Retail", [("shop", "clothes")], "clothing-brand"),
    "Boutique":                 ("Retail", [("shop", "boutique"), ("shop", "clothes")], "clothing-brand"),
    "Shoe Store":               ("Retail", [("shop", "shoes")], "shoe-store"),
    "Jewellery Store":          ("Retail", [("shop", "jewelry")], "jewelry"),
    "Watch Store / Repair":     ("Retail", [("shop", "watches"), ("craft", "watchmaker")], "jewelry"),
    "Cosmetics Store":          ("Retail", [("shop", "cosmetics"), ("shop", "perfumery")], "skincare-brand"),
    "Furniture Store":          ("Retail", [("shop", "furniture")], "furniture"),
    "Home Decor":               ("Retail", [("shop", "houseware"), ("shop", "interior_decoration")], "home-decor"),
    "Electronics Store":        ("Retail", [("shop", "electronics")], "electronics-store"),
    "Mobile Phone Store":       ("Retail", [("shop", "mobile_phone")], "mobile-store"),
    "Computer / Repair Shop":   ("Retail", [("shop", "computer"), ("shop", "computer_repair"), ("shop", "mobile_phone_repair")], "electronics-store"),
    "Grocery / Convenience":    ("Retail", [("shop", "convenience"), ("shop", "grocery")], "grocery-store"),
    "Supermarket":              ("Retail", [("shop", "supermarket")], "supermarket"),
    "Organic Store":            ("Retail", [("shop", "organic"), ("shop", "health_food")], "organic-store"),
    "Pet Store":                ("Retail", [("shop", "pet")], "pet-store"),
    "Pet Grooming":             ("Retail", [("shop", "pet_grooming")], "pet-grooming"),
    "Pet Boarding":             ("Retail", [("amenity", "animal_boarding")], "pet-boarding"),
    "Dog Training":             ("Retail", [("amenity", "animal_training")], "dog-training"),
    "Bookstore":                ("Retail", [("shop", "books")], "bookstore"),
    "Toy Store":                ("Retail", [("shop", "toys")], "toy-store"),
    "Gift Shop":                ("Retail", [("shop", "gift")], "gift-shop"),
    "Stationery Shop":          ("Retail", [("shop", "stationery")], "print-shop"),
    "Sports Shop":              ("Retail", [("shop", "sports")], "shoe-store"),
    "Bicycle Shop":             ("Retail", [("shop", "bicycle")], "motorcycle"),
    "Florist":                  ("Retail", [("shop", "florist")], "florist"),
    "Garden Centre / Nursery":  ("Retail", [("shop", "garden_centre"), ("shop", "nursery")], "plant-nursery"),
    "Hardware Store":           ("Retail", [("shop", "hardware"), ("shop", "doityourself")], "electronics-store"),
    "Antique Shop":             ("Retail", [("shop", "antiques")], "home-decor"),
    "Second-hand / Charity":    ("Retail", [("shop", "second_hand"), ("shop", "charity")], "clothing-brand"),
    "Tailor / Alterations":     ("Retail", [("craft", "tailor"), ("shop", "tailor"), ("craft", "dressmaker")], "clothing-brand"),
    "Shoe Repair":              ("Retail", [("craft", "shoemaker"), ("shop", "shoe_repair")], "shoe-store"),
    "Laundry / Dry Clean":      ("Retail", [("shop", "laundry"), ("shop", "dry_cleaning")], "cleaning"),

    # ── Automotive ────────────────────────────────────────────────────────
    "Car Dealership":           ("Automotive", [("shop", "car")], "car-dealer"),
    "Used Car Dealer":          ("Automotive", [("shop", "car")], "used-car-dealer"),
    "EV Dealership":            ("Automotive", [("shop", "car")], "ev-dealer"),
    "Bike / Motorcycle Dealer": ("Automotive", [("shop", "motorcycle")], "bike-dealer"),
    "Motorcycle Workshop":      ("Automotive", [("shop", "motorcycle_repair")], "motorcycle"),
    "Auto Repair Garage":       ("Automotive", [("shop", "car_repair")], "auto-repair"),
    "Tyre Shop":                ("Automotive", [("shop", "tyres")], "tyre-shop"),
    "Car Wash":                 ("Automotive", [("amenity", "car_wash")], "car-wash"),
    "Car Detailing":            ("Automotive", [("shop", "car_repair")], "car-detailing"),
    "Car Rental":               ("Automotive", [("amenity", "car_rental")], "car-dealer"),
    "Taxi Company":             ("Automotive", [("amenity", "taxi"), ("office", "taxi")], "logistics-company"),
    "Towing Service":           ("Automotive", [("shop", "car_repair")], "towing"),
    "EV Charging Network":      ("Automotive", [("amenity", "charging_station")], "ev-dealer"),

    # ── Home services & trades ────────────────────────────────────────────
    "Plumber":                  ("Home Services", [("craft", "plumber")], "plumber"),
    "Electrician":              ("Home Services", [("craft", "electrician")], "electrician"),
    "HVAC / Heating":           ("Home Services", [("craft", "hvac"), ("craft", "heating_engineer")], "hvac"),
    "AC Repair & Service":      ("Home Services", [("craft", "hvac")], "ac-repair"),
    "Roofer":                   ("Home Services", [("craft", "roofer")], "roofing"),
    "Carpenter / Joiner":       ("Home Services", [("craft", "carpenter"), ("craft", "joiner"), ("craft", "cabinet_maker")], "carpenter"),
    "Painter / Decorator":      ("Home Services", [("craft", "painter")], "painter"),
    "Plasterer":                ("Home Services", [("craft", "plasterer")], "renovation"),
    "Tiler":                    ("Home Services", [("craft", "tiler")], "renovation"),
    "Flooring":                 ("Home Services", [("craft", "floorer"), ("craft", "parquet_layer")], "renovation"),
    "Glazier / Windows":        ("Home Services", [("craft", "glaziery"), ("craft", "window_construction")], "renovation"),
    "Locksmith":                ("Home Services", [("craft", "locksmith"), ("shop", "locksmith")], "locksmith"),
    "Gardener / Landscaper":    ("Home Services", [("craft", "gardener")], "landscaping"),
    "Cleaning Service":         ("Home Services", [("craft", "cleaning"), ("shop", "cleaning")], "cleaning"),
    "Pest Control":             ("Home Services", [("craft", "pest_control")], "pest-control"),
    "Chimney Sweep":            ("Home Services", [("craft", "chimney_sweeper")], "hvac"),
    "Scaffolder":               ("Home Services", [("craft", "scaffolder")], "construction"),
    "Stonemason":               ("Home Services", [("craft", "stonemason")], "construction"),
    "Metalworker / Welder":     ("Home Services", [("craft", "metal_construction"), ("craft", "blacksmith")], "steel-manufacturer"),
    "Upholsterer":              ("Home Services", [("craft", "upholsterer")], "furniture"),
    "Solar Installer":          ("Home Services", [("craft", "solar")], "solar"),
    "Pool Service":             ("Home Services", [("craft", "pool_maintenance")], "pool-service"),
    "Water Purifier / RO":      ("Home Services", [("shop", "water")], "ro-service"),
    "Security Company":         ("Home Services", [("office", "security")], "security-services"),
    "Moving Company":           ("Home Services", [("office", "moving_company")], "moving"),

    # ── Professional & creative services ──────────────────────────────────
    "Marketing Agency":         ("Professional", [("office", "advertising_agency"), ("office", "marketing")], "marketing-agency"),
    "SEO Agency":               ("Professional", [("office", "advertising_agency")], "seo-agency"),
    "Web Design Studio":        ("Professional", [("office", "it"), ("office", "web_design")], "web-design"),
    "Branding Studio":          ("Professional", [("office", "graphic_design")], "branding-studio"),
    "IT Company":               ("Professional", [("office", "it")], "it-company"),
    "SaaS Company":             ("Professional", [("office", "it")], "saas-company"),
    "IT Support":               ("Professional", [("office", "it")], "it-support"),
    "BPO / Call Centre":        ("Professional", [("office", "telecommunication")], "bpo"),
    "Consulting":               ("Professional", [("office", "consulting")], "consulting"),
    "HR Consulting":            ("Professional", [("office", "employment_agency")], "hr-consulting"),
    "Recruitment Agency":       ("Professional", [("office", "employment_agency")], "recruitment"),
    "Translation Service":      ("Professional", [("office", "translator")], "translation"),
    "Photography Studio":       ("Professional", [("craft", "photographer"), ("shop", "photo")], "photography"),
    "Wedding Photography":      ("Professional", [("craft", "photographer")], "wedding-photography"),
    "Video Production":         ("Professional", [("craft", "photographer"), ("office", "film_production")], "videography"),
    "Podcast Studio":           ("Professional", [("studio", "audio")], "podcast-studio"),
    "Print Shop":               ("Professional", [("shop", "copyshop"), ("shop", "printing")], "print-shop"),
    "Printing Press":           ("Professional", [("craft", "printer")], "printing-press"),
    "Copywriting Studio":       ("Professional", [("office", "advertising_agency")], "copywriting"),
    "Picture Framer":           ("Professional", [("craft", "frame_maker"), ("shop", "frame")], "home-decor"),
    "Art Gallery / Studio":     ("Professional", [("shop", "art"), ("tourism", "gallery")], "branding-studio"),

    # ── Travel & events ───────────────────────────────────────────────────
    "Travel Agency":            ("Travel & Events", [("shop", "travel_agency")], "travel-agency"),
    "Tour Operator":            ("Travel & Events", [("office", "tour_operator"), ("shop", "travel_agency")], "tour-operator"),
    "Adventure Tours":          ("Travel & Events", [("shop", "outdoor"), ("office", "tour_operator")], "adventure-tours"),
    "Visa Consultant":          ("Travel & Events", [("office", "visa")], "visa-consultant"),
    "Event Venue":              ("Travel & Events", [("amenity", "events_venue")], "event-venue"),
    "Banquet Hall":             ("Travel & Events", [("amenity", "events_venue")], "banquet-hall"),
    "Wedding Venue":            ("Travel & Events", [("amenity", "events_venue")], "wedding-venue"),
    "Wedding Planner":          ("Travel & Events", [("office", "wedding_planner")], "wedding-planner"),
    "Wedding Decorator":        ("Travel & Events", [("shop", "party")], "wedding-decorator"),
    "Bridal Makeup":            ("Travel & Events", [("shop", "beauty")], "bridal-makeup"),
    "Event Management":         ("Travel & Events", [("office", "event_management")], "event-management"),
    "Event Rentals":            ("Travel & Events", [("shop", "party"), ("shop", "rental")], "event-rentals"),
    "DJ & Entertainment":       ("Travel & Events", [("office", "event_management")], "dj-entertainment"),

    # ── Entertainment & leisure ───────────────────────────────────────────
    "Cinema":                   ("Entertainment", [("amenity", "cinema")], "event-venue"),
    "Gaming Center":            ("Entertainment", [("leisure", "amusement_arcade"), ("amenity", "internet_cafe")], "event-venue"),
    "Escape Room":              ("Entertainment", [("leisure", "escape_game")], "event-venue"),
    "Bowling Alley":            ("Entertainment", [("leisure", "bowling_alley")], "event-venue"),
    "Amusement Park":           ("Entertainment", [("tourism", "theme_park")], "adventure-tours"),
    "Museum":                   ("Entertainment", [("tourism", "museum")], "event-venue"),

    # ── Manufacturing & industrial ────────────────────────────────────────
    "Textile Manufacturer":     ("Manufacturing", [("craft", "textile"), ("industrial", "textile")], "textile-manufacturer"),
    "Garment Factory":          ("Manufacturing", [("industrial", "garment"), ("man_made", "works")], "textile-manufacturer"),
    "Furniture Manufacturer":   ("Manufacturing", [("craft", "cabinet_maker"), ("industrial", "furniture")], "furniture-manufacturer"),
    "Steel & Metal Works":      ("Manufacturing", [("industrial", "steel"), ("industrial", "foundry")], "steel-manufacturer"),
    "Plastics Manufacturer":    ("Manufacturing", [("industrial", "plastic")], "plastics-manufacturer"),
    "Chemical Manufacturer":    ("Manufacturing", [("industrial", "chemical")], "chemical-manufacturer"),
    "Food Processing":          ("Manufacturing", [("industrial", "food"), ("man_made", "works")], "food-processing"),
    "Pharma Manufacturer":      ("Manufacturing", [("industrial", "pharmaceutical")], "pharma-manufacturer"),
    "Packaging Company":        ("Manufacturing", [("industrial", "packaging")], "packaging-company"),
    "Factory / Works":          ("Manufacturing", [("man_made", "works"), ("landuse", "industrial")], "food-processing"),
    "Industrial Supplier":      ("Manufacturing", [("shop", "trade"), ("shop", "industrial")], "packaging-company"),
    "Machinery Supplier":       ("Manufacturing", [("shop", "machinery"), ("shop", "agrarian")], "packaging-company"),

    # ── Logistics ─────────────────────────────────────────────────────────
    "Courier Service":          ("Logistics", [("amenity", "post_office"), ("office", "courier")], "logistics-company"),
    "Logistics Company":        ("Logistics", [("office", "logistics")], "logistics-company"),
    "Freight Forwarder":        ("Logistics", [("office", "forwarding_agency"), ("office", "logistics")], "freight-forwarder"),
    "Warehouse":                ("Logistics", [("building", "warehouse"), ("landuse", "logistics")], "logistics-company"),

    # ── Agriculture ───────────────────────────────────────────────────────
    "Farm":                     ("Agriculture", [("place", "farm"), ("landuse", "farmyard")], "agro-company"),
    "Dairy Farm":               ("Agriculture", [("shop", "dairy"), ("landuse", "farmyard")], "dairy-farm"),
    "Poultry Farm":             ("Agriculture", [("landuse", "farmyard")], "poultry-farm"),
    "Plant Nursery":            ("Agriculture", [("shop", "garden_centre"), ("landuse", "plant_nursery")], "plant-nursery"),
    "Agri Company":             ("Agriculture", [("shop", "agrarian")], "agro-company"),

    # ── Community & public ────────────────────────────────────────────────
    "Temple":                   ("Community", [("building", "temple"), ("religion", "hindu")], "temple"),
    "Ashram / Retreat":         ("Community", [("amenity", "monastery")], "ashram"),
    "Church":                   ("Community", [("building", "church"), ("religion", "christian")], "church"),
    "Mosque":                   ("Community", [("building", "mosque"), ("religion", "muslim")], "mosque"),
    "Gurudwara":                ("Community", [("religion", "sikh")], "gurudwara"),
    "NGO / Charity":            ("Community", [("office", "ngo"), ("office", "charity")], "ngo-trust"),
    "Community Organisation":   ("Community", [("amenity", "community_centre"), ("office", "association")], "ngo-trust"),
    "Funeral Director":         ("Community", [("shop", "funeral_directors")], "ngo-trust"),
    "Government Office":        ("Community", [("office", "government")], "ngo-trust"),
}

# ── derived lookups ───────────────────────────────────────────────────────
NICHES = {name: tags for name, (_seg, tags, _f) in CATALOGUE.items()}
SEGMENTS = {name: seg for name, (seg, _t, _f) in CATALOGUE.items()}
FOUNDRY = {name: slug for name, (_s, _t, slug) in CATALOGUE.items() if slug}

FOUNDRY_BASE = "https://foundry.ripplecheck.io"

# ── Foundry personalised-preview link ────────────────────────────────────
# Foundry builds the preview from the URL itself — nothing is stored on a
# server — so Lead Finder can generate the exact link it needs.
#
# ── CONTRACT WITH FOUNDRY — do not change one side without the other ─────
#
# Foundry is a static site on shared hosting with no database. Everything it
# needs to personalise a demo must travel inside the URL.
#
# Payload:   BusinessName|Phone|City|TradeSlug|AgencyName
# Encoding:  UTF-8 -> base64url, padding stripped
# Param:     ?d=
# Endpoint:  https://foundry.ripplecheck.io/{demo|app}/{trade-slug}/?d=<token>
#
# Worked example:
#   raw    Modern Beauty Salon|+91-904-502-1076|Delhi|beauty-salon|Matrix Devs
#   url    https://foundry.ripplecheck.io/app/beauty-salon/?d=TW9kZXJuIEJlYXV0...
#
# Note the trade field carries the *slug* (beauty-salon), not the display name
# (Beauty Salon) — Foundry uses it to pick the template, so it has to match the
# folder name in the URL exactly.
#
# Why encode at all:
#   * One parameter instead of five, so the link survives being pasted into
#     WhatsApp, Instagram and SMS with nothing mangling the &s.
#   * Non-Latin names (Hindi, Arabic, Thai) pass through intact because the
#     payload is UTF-8 encoded before base64.
#   * base64url (- and _ rather than + and /) with padding stripped means the
#     token needs no percent-escaping at all.
#
# What this is NOT: encryption. Base64 is reversible by anyone in one line.
# Never put anything private in here — it is public data in a public link.

FOUNDRY_PARAM = "d"
FOUNDRY_FIELDS = ["business", "phone", "city", "trade", "agency"]
_SEP = "|"

# Your agency name, shown on the personalised demo. Set from the Settings panel.
AGENCY = {"name": ""}


def set_agency(name):
    AGENCY["name"] = (name or "").strip()


def _clean(v):
    """Make one field safe for a pipe-delimited payload."""
    if not v:
        return ""
    s = str(v).replace("\r", " ").replace("\n", " ").strip()
    s = s.replace(_SEP, "/")          # a literal pipe would break the split
    return " ".join(s.split())        # collapse runs of whitespace


def encode_payload(business="", phone="", city="", trade="", agency=None):
    """
    BusinessName|Phone|City|TradeSlug|AgencyName -> base64url token, unpadded.

    `trade` must already be the Foundry slug. `agency` defaults to whatever the
    Settings panel has stored.
    """
    import base64
    if agency is None:
        agency = AGENCY.get("name", "")
    raw = _SEP.join(_clean(v) for v in (business, phone, city, trade, agency))
    raw = raw.rstrip(_SEP)            # drop trailing empties for a shorter link
    token = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
    return token.rstrip("=")          # padding is optional and just noise


def decode_payload(token):
    """Reverse of encode_payload. Returns a dict; {} if the token is malformed."""
    import base64
    if not token:
        return {}
    try:
        pad = "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(token + pad).decode("utf-8")
    except Exception:
        return {}
    parts = raw.split(_SEP)
    parts += [""] * (len(FOUNDRY_FIELDS) - len(parts))
    return dict(zip(FOUNDRY_FIELDS, parts))


def _foundry_url(kind, niche, business="", city="", phone="", agency=None):
    """
    kind is 'demo' (marketing site) or 'app' (SaaS dashboard).
    The slug appears twice on purpose: once as the path so Foundry serves the
    right template, once inside the payload so the page knows its own trade.
    """
    slug = FOUNDRY.get(niche)
    if not slug:
        return None
    url = f"{FOUNDRY_BASE}/{kind}/{slug}/"
    if not any((business, city, phone)):
        return url                       # nothing to personalise, plain demo
    token = encode_payload(business=business, phone=phone, city=city,
                           trade=slug, agency=agency)
    return f"{url}?{FOUNDRY_PARAM}={token}"


def foundry_demo(niche, business="", city="", phone="", agency=None, **_):
    """Live website demo, personalised when lead details are supplied."""
    return _foundry_url("demo", niche, business, city, phone, agency)


def foundry_app(niche, business="", city="", phone="", agency=None, **_):
    """Matching SaaS dashboard demo, personalised the same way."""
    return _foundry_url("app", niche, business, city, phone, agency)


def foundry_links(niche, business="", city="", phone="", agency=None):
    """Both links plus the shared token — what the dashboard button uses."""
    slug = FOUNDRY.get(niche)
    if not slug:
        return {}
    return {
        "foundry_slug": slug,
        "foundry_token": encode_payload(business=business, phone=phone,
                                        city=city, trade=slug, agency=agency),
        "foundry_demo": _foundry_url("demo", niche, business, city, phone, agency) or "",
        "foundry_app": _foundry_url("app", niche, business, city, phone, agency) or "",
    }


def segments():
    """{segment: [niche, ...]} for grouped dropdowns."""
    out = {}
    for name, seg in sorted(SEGMENTS.items()):
        out.setdefault(seg, []).append(name)
    return out
