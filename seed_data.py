import sqlite3
from werkzeug.security import generate_password_hash
from database import get_db, init_db

def seed_all():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # Clear existing data and reset sequence
    cursor.execute("DELETE FROM notifications;")
    cursor.execute("DELETE FROM reviews;")
    cursor.execute("DELETE FROM messages;")
    cursor.execute("DELETE FROM project_discussions;")
    cursor.execute("DELETE FROM projects;")
    cursor.execute("DELETE FROM bookings;")
    cursor.execute("DELETE FROM portfolio_videos;")
    cursor.execute("DELETE FROM creator_services;")
    cursor.execute("DELETE FROM creator_skills;")
    cursor.execute("DELETE FROM creator_profiles;")
    cursor.execute("DELETE FROM users;")
    try:
        cursor.execute("DELETE FROM sqlite_sequence;")
    except Exception:
        pass

    # 1. Seed Users (with explicit IDs 1..8)
    default_pw_admin = generate_password_hash("admin123")
    default_pw_creator = generate_password_hash("creator123")
    default_pw_customer = generate_password_hash("customer123")

    users_data = [
        # Admin (ID 1)
        (1, "admin@adconnect.com", default_pw_admin, "Platform Administrator", "admin",
         "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80",
         "Super Admin governing ADCONNECT operations, user moderation, and financial flows.",
         "ADCONNECT HQ", "+1-800-555-0199", "San Francisco, USA", 1),

        # Creators (IDs 2, 3, 4, 5)
        (2, "alex.motion@adconnect.com", default_pw_creator, "Alex Rivera", "creator",
         "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
         "Lead 3D & VFX Motion Director. 8+ years crafting high-converting CGI product commercials for Apple, Nike, and global tech disruptors.",
         "Rivera VFX Studio", "+1-310-555-4921", "Los Angeles, CA", 1),

        (3, "sarah.ugc@adconnect.com", default_pw_creator, "Sarah Chen", "creator",
         "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80",
         "Viral TikTok & UGC Video Producer. Generated 45M+ views for DTC e-commerce, beauty, and mobile apps with hook-driven storytelling.",
         "Chen Media Lab", "+1-212-555-3819", "New York, NY", 1),

        (4, "marcus.tech@adconnect.com", default_pw_creator, "Marcus Vance", "creator",
         "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",
         "Cinematic Tech & SaaS Commercial Producer. Specializing in sleek hardware renders, UI micro-animations, and investor pitch teasers.",
         "Vance Digital Labs", "+1-415-555-8290", "San Francisco, CA", 1),

        (5, "elena.fashion@adconnect.com", default_pw_creator, "Elena Rossi", "creator",
         "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80",
         "Fashion, Luxury & Cosmetics Ad Director. Editorial visual styling, vibrant color grading, and Instagram-first promotional videos.",
         "Studio Rossi Milano", "+44-20-7946-0912", "London & Milan", 1),

        # Customers (IDs 6, 7, 8)
        (6, "david.brand@gmail.com", default_pw_customer, "David Miller", "customer",
         "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&auto=format&fit=crop&q=80",
         "Founder & CEO at Lumina Smart Wearables. Innovating AR audio glasses.",
         "Lumina Vision Labs", "+1-512-555-9012", "Austin, TX", 1),

        (7, "rachel.green@velox.io", default_pw_customer, "Rachel Green", "customer",
         "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&auto=format&fit=crop&q=80",
         "Head of Growth & Performance Marketing at Velox Energy Drink.",
         "Velox Global Brands", "+1-305-555-7381", "Miami, FL", 1),

        (8, "kevin.startup@pulse.ai", default_pw_customer, "Kevin Zhang", "customer",
         "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&auto=format&fit=crop&q=80",
         "Product Marketing Lead at Pulse AI - Next-gen enterprise intelligence.",
         "Pulse Technologies", "+1-206-555-1425", "Seattle, WA", 1),
    ]

    for u in users_data:
        cursor.execute("""
        INSERT INTO users (id, email, password_hash, full_name, role, avatar_url, bio, company_name, phone, location, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, u)

    # 2. Creator Profiles
    creator_profiles = [
        (2, "3D Motion Graphics & CGI Commercial Director", 8, 85.0, 1, 1, "@alexrivera_vfx", "youtube.com/@riveravfx", "riveravfx.studio", 4.95, 28, 42),
        (3, "Viral UGC & Social Commerce Ad Expert", 4, 60.0, 1, 1, "@sarahchen_ugc", "youtube.com/@chenmedialab", "chenmedialab.com", 4.90, 36, 68),
        (4, "High-Tech Hardware & SaaS Commercial Specialist", 7, 95.0, 1, 1, "@marcusvance_tech", "youtube.com/@vancedigital", "vancedigital.io", 4.98, 19, 31),
        (5, "Luxury Fashion & Cosmetics Video Creator", 6, 75.0, 1, 0, "@elenarossi_style", "youtube.com/@studiorossi", "studiorossimilano.com", 4.88, 22, 39),
    ]

    for cp in creator_profiles:
        cursor.execute("""
        INSERT INTO creator_profiles (user_id, tagline, experience_years, hourly_rate, verified, featured, instagram_url, youtube_url, website_url, rating_avg, rating_count, completed_projects_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, cp)

    # 3. Creator Skills
    skills_data = [
        # Alex Rivera (ID 2)
        (2, "3D Motion Graphics"), (2, "Cinema 4D & Octane"), (2, "Product Animation"), (2, "VFX & Compositing"), (2, "4K Color Grading"), (2, "Houdini Simulations"),
        # Sarah Chen (ID 3)
        (3, "TikTok & Reels Ads"), (3, "UGC Direct Response"), (3, "Hook Ideation"), (3, "Voiceover & Scripting"), (3, "E-commerce Video Ads"), (3, "CapCut Pro"),
        # Marcus Vance (ID 4)
        (4, "Tech Commercials"), (4, "3D Hardware Exploded Views"), (4, "SaaS Promo Videos"), (4, "Blender & Unreal Engine"), (4, "Sound Design"), (4, "Storyboard Design"),
        # Elena Rossi (ID 5)
        (5, "Fashion Brand Commercials"), (5, "Beauty & Skincare Ads"), (5, "Art Direction"), (5, "Editorial Visuals"), (5, "Cinematic Lighting"), (5, "Social Lookbooks"),
    ]
    for s in skills_data:
        cursor.execute("INSERT INTO creator_skills (user_id, skill_name) VALUES (?, ?)", s)

    # 4. Creator Services / Packages
    services_data = [
        # Alex Rivera
        (2, "basic", "Social 3D Teaser (10-15s)", "High-impact 3D loop animation with custom textures, lighting, and sound effects for Instagram/TikTok.", 350.0, 3, 2),
        (2, "standard", "Full 3D Product Commercial (30s)", "Complete commercial with 3D product modeling, dynamic camera cuts, text callouts, sound design & 4K master.", 750.0, 6, 3),
        (2, "premium", "Cinematic Multi-Format Ad Suite (60s)", "Full brand campaign: 60s master ad + 3 cutdowns (15s vertical, 30s widescreen) with custom soundtrack and revisions.", 1500.0, 10, 5),

        # Sarah Chen
        (3, "basic", "Single Viral UGC Hook Video (15s)", "Engaging organic-style TikTok/Reel with hook, product demonstration, caption overlays, and CTA.", 200.0, 2, 2),
        (3, "standard", "3x High-Converting UGC Variations (30s)", "Three distinct hook variations with the same core body & CTA to A/B test on Meta and TikTok ads.", 450.0, 4, 3),
        (3, "premium", "Ultimate UGC Ads Bundle (5 Videos + Raw)", "Five full UGC scripts and variations, voiceover, hooks, raw footage included, and rights for paid ads.", 900.0, 7, 4),

        # Marcus Vance
        (4, "basic", "SaaS Feature Highlight Video (20s)", "Crisp UI walkthrough with slick zooms, animated cursor, and motion typography.", 400.0, 3, 2),
        (4, "standard", "3D Tech Product Reveal (30s-45s)", "Photorealistic 3D hardware assembly, exploded part views, glowing HUD accents, and voiceover sync.", 1100.0, 7, 3),
        (4, "premium", "Enterprise Brand Teaser & Demo (90s)", "Complete investor-grade product film with 3D environment, actor/voiceover, custom score, and 4K deliverables.", 2400.0, 14, 5),

        # Elena Rossi
        (5, "basic", "Minimalist Beauty Reel (15s)", "Macro beauty/product aesthetic shots with chic typography, transitions, and licensed music.", 280.0, 3, 2),
        (5, "standard", "Fashion Editorial Brand Story (30s)", "High-fashion lookbook ad with model, studio lighting, dynamic color grading, and vertical format.", 680.0, 5, 3),
        (5, "premium", "Full Runway & Collection Film (60s)", "Cinematic collection showcase, multiple outfits/products, drone & studio b-roll, 4K & multi-aspect exports.", 1600.0, 9, 4),
    ]
    for srv in services_data:
        cursor.execute("""
        INSERT INTO creator_services (user_id, tier, title, description, price, delivery_days, revisions_allowed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, srv)

    # 5. Portfolio Videos
    portfolio_videos = [
        # Alex Rivera (ID 2)
        (2, "Apex Smartwatch - 3D Hologram Ad", "Futuristic 3D product commercial showcasing titanium finish and holographic UI.", "3D Animation",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
         "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80", "0:30", 1420, 1),

        (2, "Nova Earbuds - Sound in Motion", "Dynamic liquid sound wave simulation and explosion render for high-end audio brand.", "Tech",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
         "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80", "0:25", 980, 1),

        (2, "CyberSneaker 2099 - Cyberpunk CGI", "Neon city streets product drop trailer with particle effects and metallic reflections.", "3D Animation",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
         "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80", "0:45", 2100, 0),

        # Sarah Chen (ID 3)
        (3, "GlowSkin Vitamin C Serum - TikTok UGC", "Relatable before-and-after morning skincare routine hook that increased sales by 310%.", "UGC",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
         "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop&q=80", "0:32", 4800, 1),

        (3, "HydroFlask Smart Bottle - Lifestyle Reel", "Fast-paced summer beach workout video showing temperature retention demo.", "Food & Beverage",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
         "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80", "0:28", 3250, 1),

        # Marcus Vance (ID 4)
        (4, "AeroDrone X1 - Autonomous Flight Teaser", "Exploded mechanical 3D view of carbon fiber propellers and gimbal camera.", "Tech",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
         "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=600&auto=format&fit=crop&q=80", "0:52", 3400, 1),

        (4, "OmniPay Terminal - Seamless POS Commercial", "Sleek hardware lighting and tactile interaction motion graphics for FinTech.", "Corporate",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackSeeTheWorld.mp4",
         "https://images.unsplash.com/photo-1556742049-0a67e55722c6?w=600&auto=format&fit=crop&q=80", "0:35", 1650, 0),

        # Elena Rossi (ID 5)
        (5, "Aura Parfum - Velvet Nights Campaign", "Sensual cinematic lighting with gold dust bokeh and luxury glass reflections.", "Fashion & Beauty",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
         "https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&auto=format&fit=crop&q=80", "0:40", 2780, 1),

        (5, "Vogue Milano Fall Footwear Promo", "Chic Milan cobblestone catwalk pacing with modern typography and beat sync.", "Fashion & Beauty",
         "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
         "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&auto=format&fit=crop&q=80", "0:30", 1950, 0),
    ]

    for pv in portfolio_videos:
        cursor.execute("""
        INSERT INTO portfolio_videos (user_id, title, description, category, video_url, thumbnail_url, duration, views_count, featured)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, pv)

    # 6. Bookings & Projects
    # Booking 1: David -> Alex (Project 1, Stage 6)
    cursor.execute("""
    INSERT INTO bookings (id, customer_id, creator_id, service_tier, project_title, category, budget, delivery_deadline, requirement_brief, reference_urls, status)
    VALUES (1, 6, 2, 'standard', 'Lumina Audio Glasses 3D Launch Teaser', '3D Animation', 750.0, '2026-09-01',
            'We need a stunning 30-second 3D commercial for our new Lumina Smart Glasses. Focus on the titanium frames, open-ear acoustic speakers, and sleek design. Color palette: Matte Black & Cyber Cyan.',
            'https://youtube.com/watch?v=sample-glasses', 'in_progress')
    """)

    cursor.execute("""
    INSERT INTO projects (id, booking_id, customer_id, creator_id, title, category, budget, stage, status, draft_video_url, draft_notes, created_at)
    VALUES (1, 1, 6, 2, 'Lumina Audio Glasses 3D Launch Teaser', '3D Animation', 750.0, 6, 'in_review',
            'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
            'Hey David! Here is the initial 3D draft cut with full lighting, sound effects, and product turntable render. Please review and let me know if you need any adjustments to the camera speed!',
            '2026-08-15 10:00:00')
    """)

    # Booking 2: Rachel -> Sarah (Project 2, Stage 8)
    cursor.execute("""
    INSERT INTO bookings (id, customer_id, creator_id, service_tier, project_title, category, budget, delivery_deadline, requirement_brief, reference_urls, status)
    VALUES (2, 7, 3, 'standard', 'Velox Energy TikTok Summer Ad Campaign', 'UGC', 450.0, '2026-08-25',
            'High-energy TikTok ads targeting athletes & gamers. 3 hook variations showcasing the refreshing fizz, zero sugar claim, and natural caffeine kick.',
            'https://tiktok.com/@veloxenergy', 'in_progress')
    """)

    cursor.execute("""
    INSERT INTO projects (id, booking_id, customer_id, creator_id, title, category, budget, stage, status, draft_video_url, draft_notes, final_video_url, final_notes, created_at)
    VALUES (2, 2, 7, 3, 'Velox Energy TikTok Summer Ad Campaign', 'UGC', 450.0, 8, 'active',
            'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4',
            'First cut with all 3 hooks attached.',
            'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4',
            'Hi Rachel! All revisions have been incorporated. Here is the final 4K high-res deliverable ready for your ad manager campaign!',
            '2026-08-10 14:30:00')
    """)

    # Booking 3: Kevin -> Marcus (Project 3, Stage 9)
    cursor.execute("""
    INSERT INTO bookings (id, customer_id, creator_id, service_tier, project_title, category, budget, delivery_deadline, requirement_brief, reference_urls, status)
    VALUES (3, 8, 4, 'standard', 'Pulse AI Enterprise Analytics Commercial', 'Tech', 1100.0, '2026-08-12',
            '30s tech film showcasing Pulse AI automated data pipelines. Needs sleek neon HUD graphics and fast-paced editing.',
            'https://pulse.ai/demo', 'completed')
    """)

    cursor.execute("""
    INSERT INTO projects (id, booking_id, customer_id, creator_id, title, category, budget, stage, status, draft_video_url, draft_notes, final_video_url, final_notes, created_at, completed_at)
    VALUES (3, 3, 8, 4, 'Pulse AI Enterprise Analytics Commercial', 'Tech', 1100.0, 9, 'completed',
            'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4',
            'Draft render for data flows.',
            'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackSeeTheWorld.mp4',
            'Delivered full resolution master package with vertical 9:16 and widescreen 16:9 versions.',
            '2026-08-01 09:00:00', '2026-08-12 16:00:00')
    """)

    # Booking 4: Rachel -> Elena (Pending Booking Request)
    cursor.execute("""
    INSERT INTO bookings (id, customer_id, creator_id, service_tier, project_title, category, budget, delivery_deadline, requirement_brief, reference_urls, status)
    VALUES (4, 7, 5, 'basic', 'Velox Glow - Botanical Infusion Video Reel', 'Fashion & Beauty', 280.0, '2026-09-10',
            'We are launching a limited edition botanical flavor. We want an elegant aesthetic 15s reel focusing on the glass bottle and herbal ingredients.',
            'https://velox.io/botanical', 'pending')
    """)

    # 7. Reviews
    cursor.execute("""
    INSERT INTO reviews (project_id, customer_id, creator_id, rating, review_text, created_at)
    VALUES (3, 8, 4, 5,
            'Marcus was exceptional from start to finish! The 3D HUD animations and sound design elevated our AI product commercial beyond expectations. Our click-through rate jumped 45% on day one of launching the ad. Highly recommend!',
            '2026-08-13 11:20:00')
    """)

    # 8. Project Discussions
    discussions = [
        (1, 6, "Hi Alex! Excited to work together. Let me know once you have the initial 3D storyboard ready."),
        (1, 2, "Thanks David! Working on the lighting pass right now. I'll have the draft uploaded by tonight for your review."),
        (2, 7, "Sarah, the hook in variation #2 is pure gold. Can we just make the brand logo appear 1 second earlier?"),
        (2, 3, "Done! I tweaked the timing and uploaded the final version below. Check it out!"),
    ]
    for d in discussions:
        cursor.execute("INSERT INTO project_discussions (project_id, sender_id, message) VALUES (?, ?, ?)", d)

    # 9. Direct Messages
    messages = [
        (6, 2, "Hey Alex, saw your latest 3D reel on the platform. Incredible work!", 1),
        (2, 6, "Thank you David! Really appreciate the kind words. Excited to collaborate on Lumina!", 1),
        (7, 3, "Hey Sarah, are you available for a 3-video UGC package this month?", 1),
        (3, 7, "Absolutely Rachel! Feel free to send over the booking request with your product details.", 1),
    ]
    for m in messages:
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, content, is_read) VALUES (?, ?, ?, ?)", m)

    # 10. Notifications
    notifications = [
        (6, "Draft Video Ready", "Alex Rivera uploaded a new draft video for 'Lumina Audio Glasses 3D Launch Teaser'.", "/customer/project/1", "project", 0),
        (7, "Final Video Delivered", "Sarah Chen delivered the final advertisement for 'Velox Energy TikTok Summer Ad Campaign'.", "/customer/project/2", "project", 0),
        (5, "New Booking Request", "You received a new booking request from Rachel Green for $280.", "/creator/bookings", "booking", 0),
        (2, "Project In Review", "David Miller is currently reviewing your draft submission.", "/creator/project/1", "project", 1),
    ]
    for n in notifications:
        cursor.execute("INSERT INTO notifications (user_id, title, message, link_url, type, is_read) VALUES (?, ?, ?, ?, ?, ?)", n)

    conn.commit()
    conn.close()
    print("[SEED] Successfully seeded rich mock data for ADCONNECT platform!")

if __name__ == '__main__':
    seed_all()
