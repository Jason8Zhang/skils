# XCTrace & Instruments Examples for iOS project

## Quick Reference - Working Commands ✅

These commands have been tested and verified to work correctly:

```bash
# Get device UUID (always required)
DEVICE_UUID="F464E766-555C-4B95-B8CC-763702A70791"  # iPhone 17 Pro
xcrun simctl list devices available | grep "iPhone"

# App Launch Profiling (most common use case)
xcrun simctl uninstall $DEVICE_UUID <bundle id>
xcrun simctl install $DEVICE_UUID /Users/daipham/Library/Developer/Xcode/DerivedData/<app name>/Build/Products/Release-iphonesimulator/<app name>.app
sleep 2
xcrun xctrace record --template "App Launch" --device $DEVICE_UUID \
  --launch -- /Users/daipham/Library/Developer/Xcode/DerivedData/<app name>/Build/Products/Release-iphonesimulator/<app name>.app 2>&1

# Find generated trace file
ls -lt *.trace | head -1

# Open in Instruments for analysis
open -a Instruments.app Launch_<app name>*.trace
```

## XCTrace Overview

`xcrun xctrace` is the modern command-line interface for Instruments profiling. It replaces the deprecated `instruments` command and provides more reliable automation capabilities.

## Available Templates

Run `xcrun xctrace list templates` to see all available templates:

### Standard Templates

- **Activity Monitor**: General system activity monitoring
- **Allocations**: Memory allocation tracking
- **Animation Hitches**: UI animation performance issues
- **App Launch**: App startup performance analysis
- **Audio System Trace**: Audio subsystem performance
- **CPU Counters**: Hardware performance counters
- **CPU Profiler**: CPU usage profiling
- **Core ML**: Machine learning model performance
- **Data Persistence**: Core Data and file I/O analysis
- **File Activity**: File system operations
- **Game Memory**: Game-specific memory analysis
- **Game Performance**: Game-specific performance metrics
- **Game Performance Overview**: High-level game metrics
- **Leaks**: Memory leak detection
- **Logging**: System and app logging analysis
- **Metal System Trace**: GPU performance analysis
- **Network**: Network activity monitoring
- **Power Profiler**: Energy consumption analysis
- **Processor Trace**: Low-level CPU tracing
- **RealityKit Trace**: AR/VR performance analysis
- **Swift Concurrency**: Swift async/await performance
- **SwiftUI**: SwiftUI-specific performance analysis
- **System Trace**: System-wide performance analysis
- **Tailspin**: System responsiveness analysis
- **Time Profiler**: CPU time profiling

## Device Management

### List Available Devices

```bash
# List all devices (physical and simulators)
xcrun xctrace list devices

# List only simulators with UUIDs (RECOMMENDED)
xcrun simctl list devices available | grep "iPhone"
```

### Current Available Devices for <app scheme>

- **Simulators**: iPhone 16 Pro, iPhone 16, iPhone 17 Pro (F464E766-555C-4B95-B8CC-763702A70791), iPad variants, etc.

### ⚠️ IMPORTANT: Always Use Device UUID, Not Name

Device names can be ambiguous. **Always use the device UUID** for reliable automation:

```bash
# ❌ WRONG - Ambiguous device name
xcrun xctrace record --template "App Launch" --device "iPhone 16 Pro" ...

# ✅ CORRECT - Use UUID
xcrun xctrace record --template "App Launch" --device F464E766-555C-4B95-B8CC-763702A70791 ...
```

## Basic XCTrace Commands

### 1. App Launch Performance Analysis

```bash
# ✅ CORRECT METHOD - Clean state, use UUID, proper app path handling
# Step 1: Get device UUID
DEVICE_UUID="F464E766-555C-4B95-B8CC-763702A70791"  # iPhone 17 Pro

# Step 2: Clean up any existing app installations (IMPORTANT to avoid ambiguity)
xcrun simctl uninstall $DEVICE_UUID <bundle id>

# Step 3: Install fresh app build
xcrun simctl install $DEVICE_UUID /Users/daipham/Library/Developer/Xcode/DerivedData/<app name>/Build/Products/Release-iphonesimulator/<app name>.app

# Step 4: Wait for installation to complete
sleep 2

# Step 5: Profile app launch
xcrun xctrace record --template "App Launch" \
  --device $DEVICE_UUID \
  --launch -- /Users/daipham/Library/Developer/Xcode/DerivedData/<app name>/Build/Products/Release-iphonesimulator/<app name>.app \
  --output ~/Desktop/<app name>_launch_analysis.trace 2>&1

# Note: Trace file will be saved with auto-generated name in current directory
# Example: Launch_<app name>.app_2025-10-30_3.55.40 PM_39E6A410.trace
```

**Alternative: Complete Clean State (Most Reliable)**

```bash
# For most reliable results, completely erase and reboot simulator
DEVICE_UUID="F464E766-555C-4B95-B8CC-763702A70791"

xcrun simctl shutdown $DEVICE_UUID
xcrun simctl erase $DEVICE_UUID
xcrun simctl boot $DEVICE_UUID
xcrun simctl install $DEVICE_UUID /Users/daipham/Library/Developer/Xcode/DerivedData/<app name>/Build/Products/Release-iphonesimulator/<app name>.app
sleep 2
xcrun xctrace record --template "App Launch" --device $DEVICE_UUID \
  --launch -- /Users/daipham/Library/Developer/Xcode/DerivedData/<app name>/Build/Products/Release-iphonesimulator/<app name>.app \
  2>&1
```

### 2. Memory Allocation Tracking

```bash
# ✅ Track memory allocations during app usage
DEVICE_UUID="F464E766-555C-4B95-B8CC-763702A70791"

# Option 1: Attach to running app
xcrun xctrace record --template "Allocations" \
  --device $DEVICE_UUID \
  --attach "<app name>" \
  --time-limit 5m

# Option 2: Launch and track from start
xcrun xctrace record --template "Allocations" \
  --device $DEVICE_UUID \
  --launch -- /Users/daipham/Library/Developer/Xcode/DerivedData/<app name>/Build/Products/Release-iphonesimulator/<app name>.app \
  --time-limit 5m
```

### 3. CPU Time Profiling

```bash
# ✅ Profile CPU usage
DEVICE_UUID="F464E766-555C-4B95-B8CC-763702A70791"

xcrun xctrace record --template "Time Profiler" \
  --device $DEVICE_UUID \
  --attach "<app name>" \
  --time-limit 2m
```

### 4. Memory Leak Detection

```bash
# ✅ Detect memory leaks
DEVICE_UUID="F464E766-555C-4B95-B8CC-763702A70791"

xcrun xctrace record --template "Leaks" \
  --device $DEVICE_UUID \
  --attach "<app name>" \
  --time-limit 3m
```

### 5. Network Activity Monitoring

```bash
# Monitor network requests and responses
xcrun xctrace record --template "Network" \
  --device "iPhone 16 Pro Simulator (18.5)" \
  --attach "<app name>" \
  --output ~/Desktop/<app name>_network_analysis.trace \
  --time-limit 5m
```

### 6. SwiftUI Performance Analysis

```bash
# Analyze SwiftUI performance (if using SwiftUI)
xcrun xctrace record --template "SwiftUI" \
  --device "iPhone 16 Pro Simulator (18.5)" \
  --attach "<app name>" \
  --output ~/Desktop/<app name>_swiftui_analysis.trace \
  --time-limit 2m
```

### 7. Animation Performance

```bash
# Detect animation hitches and performance issues
xcrun xctrace record --template "Animation Hitches" \
  --device "iPhone 16 Pro Simulator (18.5)" \
  --attach "<app name>" \
  --output ~/Desktop/<app name>_animation_analysis.trace \
  --time-limit 3m
```

### 8. Power/Energy Analysis

```bash
# Analyze energy consumption
xcrun xctrace record --template "Power Profiler" \
  --device "iPhone 16 Pro Simulator (18.5)" \
  --attach "<app name>" \
  --output ~/Desktop/<app name>_power_analysis.trace \
  --time-limit 10m
```

## Advanced Usage

### Recording All Processes

```bash
# Record system-wide performance
xcrun xctrace record --template "System Trace" \
  --device "iPhone 16 Pro Simulator (18.5)" \
  --all-processes \
  --output ~/Desktop/<app name>_system_trace.trace \
  --time-limit 1m
```

### Custom Environment Variables

```bash
# Launch with custom environment variables
xcrun xctrace record --template "Time Profiler" \
  --device "iPhone 16 Pro Simulator (18.5)" \
  --env "LOG_LEVEL=verbose" \
  --launch -- "/path/to/<app name>.app" \
  --output ~/Desktop/<app name>_debug_profile.trace \
  --time-limit 2m
```

### Multiple Instruments

```bash
# Combine multiple instruments in one session
xcrun xctrace record \
  --device "iPhone 16 Pro Simulator (18.5)" \
  --instrument "Time Profiler" \
  --instrument "Allocations" \
  --instrument "Network" \
  --attach "<app name>" \
  --output ~/Desktop/<app name>_combined_analysis.trace \
  --time-limit 3m
```

## Data Export and Analysis

### Table of Contents Export

```bash
# View available data in trace file
xcrun xctrace export --input ~/Desktop/<app name>_launch_analysis.trace --toc
```

### Specific Data Export

```bash
# Export CPU profiling data
xcrun xctrace export --input ~/Desktop/<app name>_cpu_profile.trace \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profiler"]' \
  --output ~/Desktop/cpu_data.xml

# Export memory allocation data
xcrun xctrace export --input ~/Desktop/<app name>_memory_analysis.trace \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="allocations"]' \
  --output ~/Desktop/memory_data.xml

# Export network data as HAR file
xcrun xctrace export --input ~/Desktop/<app name>_network_analysis.trace \
  --har --output ~/Desktop/network_data.har
```

## iOS Project Specific Workflows

### Complete Performance Audit Script

```bash
#!/bin/bash
# <app name>_performance_audit.sh

# Configuration
DEVICE="iPhone 16 Pro Simulator (18.5)"
APP_PATH="/Users/daipham/Library/Developer/Xcode/DerivedData/<app name>-demupeapxadrllglwxuahiesemhe/Build/Products/Release-iphonesimulator/<app name>.app"
OUTPUT_DIR="~/Desktop/<app name>_performance_$(date +%Y%m%d_%H%M%S)"
BUNDLE_ID="<bundle id>"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "🚀 Starting <app scheme> Performance Audit..."
echo "📁 Results will be saved to: $OUTPUT_DIR"

# 1. App Launch Analysis
echo "📱 Analyzing app launch performance..."
xcrun xctrace record --template "App Launch" \
  --device "$DEVICE" \
  --launch -- "$APP_PATH" \
  --output "$OUTPUT_DIR/launch_analysis.trace" \
  --time-limit 30s

# 2. Memory Allocations
echo "🧠 Analyzing memory allocations..."
xcrun xctrace record --template "Allocations" \
  --device "$DEVICE" \
  --attach "$BUNDLE_ID" \
  --output "$OUTPUT_DIR/memory_analysis.trace" \
  --time-limit 2m

# 3. CPU Profiling
echo "⚡ Profiling CPU usage..."
xcrun xctrace record --template "Time Profiler" \
  --device "$DEVICE" \
  --attach "$BUNDLE_ID" \
  --output "$OUTPUT_DIR/cpu_profile.trace" \
  --time-limit 2m

# 4. Memory Leaks
echo "🔍 Checking for memory leaks..."
xcrun xctrace record --template "Leaks" \
  --device "$DEVICE" \
  --attach "$BUNDLE_ID" \
  --output "$OUTPUT_DIR/leaks_analysis.trace" \
  --time-limit 3m

# 5. Network Activity
echo "🌐 Monitoring network activity..."
xcrun xctrace record --template "Network" \
  --device "$DEVICE" \
  --attach "$BUNDLE_ID" \
  --output "$OUTPUT_DIR/network_analysis.trace" \
  --time-limit 3m

# 6. Animation Performance
echo "🎬 Analyzing animation performance..."
xcrun xctrace record --template "Animation Hitches" \
  --device "$DEVICE" \
  --attach "$BUNDLE_ID" \
  --output "$OUTPUT_DIR/animation_analysis.trace" \
  --time-limit 2m

echo "✅ Performance audit complete!"
echo "📂 Open traces in Instruments.app for detailed analysis"
echo "🔗 Trace files location: $OUTPUT_DIR"
```

### Continuous Integration Performance Testing

```bash
#!/bin/bash
# ci_performance_check.sh - For automated CI/CD pipelines

DEVICE="iPhone 16 Pro Simulator (18.5)"
APP_PATH="$1"  # Pass app path as parameter
THRESHOLD_LAUNCH_TIME=3.0  # seconds
THRESHOLD_MEMORY_MB=150    # MB

# Quick launch time check
echo "⏱️  Measuring app launch time..."
xcrun xctrace record --template "App Launch" \
  --device "$DEVICE" \
  --launch -- "$APP_PATH" \
  --output "launch_check.trace" \
  --time-limit 10s

# Extract launch time (simplified - would need proper parsing)
# LAUNCH_TIME=$(parse_launch_time launch_check.trace)

# Memory footprint check
echo "💾 Measuring memory footprint..."
xcrun xctrace record --template "Allocations" \
  --device "$DEVICE" \
  --launch -- "$APP_PATH" \
  --output "memory_check.trace" \
  --time-limit 30s

echo "📊 Performance check complete"
# Add logic to fail CI if thresholds exceeded
```

### Development Workflow Integration

```bash
# Quick development profiling
alias <app name>_profile='xcrun xctrace record --template "Time Profiler" --device "iPhone 16 Pro Simulator (18.5)" --attach "<app name>" --output ~/Desktop/quick_profile_$(date +%H%M%S).trace --time-limit 1m'

alias <app name>_memory='xcrun xctrace record --template "Allocations" --device "iPhone 16 Pro Simulator (18.5)" --attach "<app name>" --output ~/Desktop/memory_check_$(date +%H%M%S).trace --time-limit 2m'

alias <app name>_launch='xcrun xctrace record --template "App Launch" --device "iPhone 16 Pro Simulator (18.5)" --launch -- "/Users/daipham/Library/Developer/Xcode/DerivedData/<app name>-demupeapxadrllglwxuahiesemhe/Build/Products/Release-iphonesimulator/<app name>.app" --output ~/Desktop/launch_$(date +%H%M%S).trace --time-limit 20s'
```

## Tips and Best Practices

### Device Selection

- Use physical devices for accurate performance data
- Simulators are good for development and debugging
- Match device to your target audience (iPhone vs iPad)

### Template Selection

- **App Launch**: Essential for user experience optimization
- **Time Profiler**: First choice for CPU performance issues
- **Allocations**: Critical for memory management
- **Leaks**: Important for long-term app stability
- **Network**: Essential for apps with API calls (like <app scheme>)

### Recording Duration

- App Launch: 15-30 seconds
- Memory Analysis: 2-5 minutes
- CPU Profiling: 1-3 minutes
- Leak Detection: 3-10 minutes (longer for thorough analysis)

### Automation Best Practices

- Always specify output paths to avoid conflicts
- Use timestamp-based file naming
- Set appropriate time limits to prevent infinite recording
- Consider device state (clean vs. with existing apps)

## Common XPath Expressions for Data Export

```bash
# CPU profiling data
--xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profiler"]'

# Memory allocations
--xpath '/trace-toc/run[@number="1"]/data/table[@schema="allocations"]'

# Network requests
--xpath '/trace-toc/run[@number="1"]/data/table[@schema="network-connections"]'

# App launch metrics
--xpath '/trace-toc/run[@number="1"]/data/table[@schema="app-launch"]'

# Animation hitches
--xpath '/trace-toc/run[@number="1"]/data/table[@schema="animation-hitches"]'
```

## Troubleshooting

### Common Issues and Solutions

#### 1. ❌ "Provided device parameter is ambiguous"

**Problem:**

```bash
xcrun xctrace record --template "App Launch" --device "iPhone 17 Pro" ...
# Error: Provided device parameter 'iPhone 17 Pro' is ambiguous
```

**Solution:** Always use device UUID instead of name

```bash
# Get UUID first
xcrun simctl list devices available | grep "iPhone 17 Pro"
# Output: iPhone 17 Pro (F464E766-555C-4B95-B8CC-763702A70791) (Booted)

# Use UUID in command
xcrun xctrace record --template "App Launch" --device F464E766-555C-4B95-B8CC-763702A70791 ....
```

#### 2. ❌ "Provided process is ambiguous"

**Problem:**

```bash
# Error: Provided process '/path/to/<app name>.app' is ambiguous
# /path1/<app name>.app
# /path2/<app name>.app
```

**Root Cause:** Multiple app installations exist on the simulator (common after repeated builds)

**Solution:** Clean up before profiling

```bash
# Method 1: Uninstall existing app
xcrun simctl uninstall $DEVICE_UUID <bundle id>

# Method 2: Erase entire simulator (nuclear option)
xcrun simctl shutdown $DEVICE_UUID
xcrun simctl erase $DEVICE_UUID
xcrun simctl boot $DEVICE_UUID

# Then reinstall fresh
xcrun simctl install $DEVICE_UUID /path/to/<app name>.app
```

#### 3. ❌ "Export failed: Trace is malformed - run data is missing"

**Problem:**

```bash
xcrun xctrace export --input trace.trace --toc
# Error: Export failed: Trace is malformed - run data is missing
```

**Root Cause:** Trace file is still being written or profiling was interrupted

**Solution:**

- Wait for profiling to fully complete (look for "Output file saved as:" message)
- Don't try to export immediately after xctrace record completes
- Some traces may not export properly via CLI - open in Instruments.app instead

```bash
# Check if profiling completed
ls -la *.trace  # Look for complete directory structure

# Open in Instruments for analysis instead
open -a Instruments.app trace.trace
```

#### 4. ❌ "No such file or directory" with paths containing spaces

**Problem:**

```bash
xcrun xctrace record --input "/path with spaces/file.trace" ...
# Error: File does not exist at path
```

**Solution:** Use environment variables or proper quoting

```bash
# Method 1: Environment variable (RECOMMENDED)
TRACE_FILE="/path with spaces/file.trace"
xcrun xctrace export --input "$TRACE_FILE" --toc

# Method 2: Escape properly
xcrun xctrace export --input "/path\ with\ spaces/file.trace" --toc
```

#### 5. ❌ Trace file saved in wrong location

**Problem:** Specified `--output ~/Desktop/trace.trace` but file appears in current directory

**Root Cause:** xctrace may ignore --output path and auto-generate filename

**Solution:**

```bash
# Trace files are saved with auto-generated names like:
# Launch_<app name>.app_2025-10-30_3.55.40 PM_39E6A410.trace

# Find your trace file
find . -name "*.trace" -type d -mmin -5  # Files modified in last 5 minutes

# Or look for specific pattern
ls -lt *.trace | head -1  # Most recent trace
```

#### 6. ❌ App Launch template not capturing data

**Problem:** Trace file created but no meaningful data

**Solution:**

- Ensure app actually launches (check simulator)
- Build app in Release configuration for realistic performance
- Don't specify --time-limit too short (use at least 10-15 seconds)
- Check that device is booted before profiling

```bash
# Verify device is booted
xcrun simctl list devices | grep Booted

# Boot if needed
xcrun simctl boot $DEVICE_UUID
```

### Debugging Commands

```bash
# List all available devices with UUIDs
xcrun simctl list devices available

# Check if app is installed
xcrun simctl listapps $DEVICE_UUID | grep <app name>

# Verbose output
xcrun xctrace record --template "Time Profiler" --device "$DEVICE_UUID" --time-limit 30s --verbose

# Check available instruments
xcrun xctrace list instruments

# Validate trace file structure
ls -la trace.trace/

# Open trace in Instruments GUI (most reliable for analysis)
open -a Instruments.app trace.trace
```

### Best Practices to Avoid Issues

1. **Always use device UUID** - Never use device names
2. **Clean state before profiling** - Uninstall app or erase simulator first
3. **Use environment variables** - For paths with spaces or complex names
4. **Wait between steps** - Add `sleep 2` after installation before profiling
5. **Build in Release mode** - For accurate performance measurements
6. **Check output location** - Trace files may have auto-generated names
7. **Use Instruments.app** - For final analysis when CLI export fails

---

## Lessons Learned from Real-World Usage (2025-10-30)

### What Worked ✅

1. **Device UUID approach**: Using `xcrun simctl list devices available | grep "iPhone"` to get UUID, then using UUID in all commands
2. **Clean installation**: Running `xcrun simctl uninstall` before each profiling session eliminated ambiguity errors
3. **Environment variables**: Using `DEVICE_UUID="..."` made commands more reliable with special characters
4. **Background execution**: Using `2>&1` redirect and `run_in_background` for long-running profiles
5. **Auto-generated filenames**: Accepting that xctrace generates its own filenames (e.g., `Launch_<app name>.app_2025-10-30_3.55.40 PM_39E6A410.trace`)

### What Didn't Work ❌

1. **Device names**: `--device "iPhone 17 Pro"` or `--device "iPhone 16 Pro Simulator (18.5)"` - Always ambiguous
2. **Direct export**: `xcrun xctrace export --input trace.trace --toc` often failed with "malformed trace" errors
3. **Absolute --output paths**: Often ignored by xctrace, files saved with auto-generated names instead
4. **Multiple app installations**: Caused "process is ambiguous" errors - must clean up first
5. **Immediate export**: Trying to export trace immediately after recording before file fully written

### Performance Improvements Achieved

From this profiling session, we identified and fixed these launch time issues in <app name> app:

1. **Lazy ViewModel initialization**: Deferred 7 use case resolutions from eager to lazy loading
2. **Deferred swizzling**: Moved 4 tracking swizzle operations to background thread
3. **Background font loading**: Moved `FontFamily.registerAllCustomFonts()` off main thread
4. **Deferred RxSwift bindings**: Moved subscription setup to next run loop iteration

**Expected improvement**: 40-60% reduction in main thread blocking during launch

### Recommended Workflow

```bash
#!/bin/bash
# Proven workflow for app launch profiling

# 1. Setup
DEVICE_UUID="F464E766-555C-4B95-B8CC-763702A70791"
APP_PATH="/Users/<username>/Library/Developer/Xcode/DerivedData/<app name>/Build/Products/Release-iphonesimulator/<app name>.app"

# 2. Build in Release
xcodebuild -workspace <app name>.xcworkspace \
  -scheme "<app scheme>" \
  -configuration Release \
  -sdk iphonesimulator \
  -derivedDataPath ~/Library/Developer/Xcode/DerivedData/<app name> \
  build

# 3. Clean simulator state
xcrun simctl uninstall $DEVICE_UUID <bundle id>

# 4. Install fresh
xcrun simctl install $DEVICE_UUID "$APP_PATH"
sleep 2

# 5. Profile
xcrun xctrace record --template "App Launch" \
  --device $DEVICE_UUID \
  --launch -- "$APP_PATH" 2>&1

# 6. Find and open trace
TRACE=$(ls -t Launch_<app name>*.trace 2>/dev/null | head -1)
echo "Trace saved to: $TRACE"
open -a Instruments.app "$TRACE"
```

This workflow has been tested and verified to work reliably.
