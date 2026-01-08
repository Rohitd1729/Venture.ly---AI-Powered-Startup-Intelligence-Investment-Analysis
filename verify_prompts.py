import sys
import os

try:
    import prompts
    print("✅ Successfully imported prompts module")
    
    required_prompts = [
        "TEAM_ANALYSIS_PROMPT",
        "PROBLEM_SOLUTION_PROMPT",
        "MARKET_ANALYSIS_PROMPT",
        "PRODUCT_TECH_PROMPT",
        "TRACTION_GTM_PROMPT",
        "RISK_ANALYSIS_PROMPT",
        "FINAL_SYNTHESIS_PROMPT",
        "STRUCTURED_METRICS_PROMPT",
        "TECHNICAL_DEEP_DIVE_PROMPT",
        "COMPREHENSIVE_INVESTMENT_ANALYSIS_PROMPT"
    ]
    
    missing = []
    for p in required_prompts:
        if hasattr(prompts, p):
            content = getattr(prompts, p)
            if content and len(content) > 50:
                print(f"✅ Found {p} ({len(content)} chars)")
            else:
                print(f"⚠️  Found {p} but content seems empty or too short")
                missing.append(p)
        else:
            print(f"❌ Missing {p}")
            missing.append(p)
            
    if missing:
        print(f"❌ Verification FAILED. Missing or invalid prompts: {missing}")
        sys.exit(1)
    else:
        print("✅ All prompts verified successfully")
        sys.exit(0)

except ImportError as e:
    print(f"❌ Failed to import prompts: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ An error occurred: {e}")
    sys.exit(1)
