[![Build Status](https://travis-ci.org/bannsec/frida-util.svg?branch=master)](https://travis-ci.org/bannsec/frida-util)

# Overview
This is meant to be a similar functionality to `frida-trace`, but to allow for easier `Stalk` functionality.

# Examples

## Windows Messages
Specifically watching Windows Messages handling

```bash
# Automatically discover Windows message handling locations and show event messages as they are handled.
frida-stalk -I notepad.exe windows_messages notepad.exe

# Only show information about windows message WM_CHAR and WM_KEYDOWN from notepad.exe
frida-stalk -I notepad.exe -rw windows_messages notepad.exe -wm WM_CHAR WM_KEYDOWN
```

## Stalking
Use Frida stalk to trace through things

```
# Only look at traces from notepad's Windows Message handler function
frida-stalk stalk notepad.exe --include-function notepad.exe:0x3a50 -I notepad.exe
```

## Find
Find things in memory.

```
# Find where your string 'hello world' is in notepad (will check for char and wchar versions)
frida-stalk find notepad.exe --string "Hello world"
```

## General Options
Replacing functions dynamically during execution
```
# Replace function located at offset 0x64a in a.out binary, returning value 0x123
frida-stalk stalk a.out -f ./a.out --resume -rf "a.out:0x64a?0x123"

# Disable alarm and ptrace functions
frida-stalk stalk test2 -f ./test2 --resume -rf ":alarm?1" ":ptrace?1"
```
