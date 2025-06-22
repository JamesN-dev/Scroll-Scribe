#!/usr/bin/env python3
"""Test what litellm attributes actually exist."""

try:
    import litellm
    print("✅ litellm imported successfully")

    # Test set_verbose
    print("\n🔍 Testing set_verbose...")
    try:
        print(f"Current set_verbose value: {getattr(litellm, 'set_verbose', 'NOT_FOUND')}")
        litellm.set_verbose = True
        print("✅ litellm.set_verbose = True works")
        litellm.set_verbose = False
        print("✅ litellm.set_verbose = False works")
    except Exception as e:
        print(f"❌ set_verbose failed: {e}")

    # Test suppress_debug_info
    print("\n🔍 Testing suppress_debug_info...")
    if hasattr(litellm, 'suppress_debug_info'):
        print("✅ suppress_debug_info exists")
        try:
            litellm.suppress_debug_info = True
            print("✅ litellm.suppress_debug_info = True works")
        except Exception as e:
            print(f"❌ suppress_debug_info failed: {e}")
    else:
        print("❌ suppress_debug_info does NOT exist")

    # Test _turn_on_debug
    print("\n🔍 Testing _turn_on_debug...")
    if hasattr(litellm, '_turn_on_debug'):
        print("✅ _turn_on_debug exists")
    else:
        print("❌ _turn_on_debug does NOT exist")

    print(f"\n📋 Available litellm attributes: {[attr for attr in dir(litellm) if not attr.startswith('__')][:10]}...")

except ImportError as e:
    print(f"❌ Failed to import litellm: {e}")
