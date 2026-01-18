# Guidance
### A conflict fixer for your Baldur's Gate 3 mods

## What does this thing do?

So here's the problem: lots of amazing mods fix bugs, bring back cut content from Early Access, or remove things that don't quite fit. To do their magic, they need to tweak dialog resources. But here's where things get messy—when two mods try to change the same dialog, only one actually wins (usually whichever one loads last). The other mod's changes just... vanish.

Guidance fixes that. It lets multiple mods peacefully coexist by merging their changes into the same dialog resource. This works for dialogs, banters, automated dialogs, and dialog timelines. (Voice barks aren't supported yet, but I'm working on it!)

Here's how it works: Guidance analyzes what each mod changed and tries to combine everything into one dialog. Since mods usually tweak different parts of the same conversation, it can usually reconstruct a dialog with everyone's changes included. If two mods happen to modify the exact same thing, Guidance uses the change from whichever mod you've marked as higher priority.

## Let's get this running

### Step 1: Get the prerequisites

You'll need .NET 8.0 installed. Don't worry — if you don't have it, Guidance will detect that and open the download page for you. Just grab .NET Runtime 8.0.23 from [here](https://dotnet.microsoft.com/en-us/download/dotnet/8.0). That's the console-only version. If you're also using Laughing Leader's BG3 Mod Manager or other modding tools, you might want the .NET Desktop Runtime 8.0.23 instead since those need the UI components.

Guidance also uses LSLib by Norbyte, but it'll download that automatically from GitHub, so you don't need to worry about it.

### Step 2: Download and launch

Grab Guidance from [GitHub releases](https://github.com/0x1amy0urdad/Guidance/releases). It's a standalone exe — no installation needed. Just put it somewhere and run it. Fair warning: Windows might get suspicious since the executable isn't signed, depending on your security settings.

When you first launch it, Guidance needs to find your Baldur's Gate 3 installation. If you're on Steam, it should find it automatically. GOG might work too. If not, you'll see a file picker asking you to locate bg3.exe.

The very first launch takes a few minutes (how long depends on your PC). I built Guidance on my Python BG3 modding library, and it needs to create an index of all BG3's internal objects and structures. Grab a coffee, it's worth the wait.

### Step 3: Pick your conflicts

I'll use [Really Shadowheart](https://www.nexusmods.com/baldursgate3/mods/11524) and [Waterproof Shadowheart](https://www.nexusmods.com/baldursgate3/mods/18548) as an example here.

Once everything loads up, you'll see the main window:

![](https://raw.githubusercontent.com/0x1amy0urdad/Guidance/refs/heads/main/images/guidance-pic1.png)

Check the boxes next to the conflicts you want to resolve. For this example, I'll mark WaterproofShadowheart/ReallyShadowheart. After you select your conflicts, you'll see a summary on the right panel.

![](https://raw.githubusercontent.com/0x1amy0urdad/Guidance/refs/heads/main/images/guidance-pic2.png)

### Step 4: Set mod priorities

Time to decide which mod is more important. I usually recommend setting heavier mods (ones that change more stuff) as top priority since the conflict resolution works better that way. Full transparency: when I made Waterproof Shadowheart the top priority, the Skinny Dipping scene got a bit buggy. I'm still working on improving the algorithm!

![](https://raw.githubusercontent.com/0x1amy0urdad/Guidance/refs/heads/main/images/guidance-pic3.png)

Technically you can resolve multiple conflicts with more than 2 mods at once, but fair warning — there are still some bugs that might cause issues.

### Step 5: Patch or merge?

Now for the important decision: do you want a patch or a merge?

**Patch:** Creates a brand new mod containing just the fixed dialogs. You keep both original mods installed and add this patch below them in your load order.

**Merge:** Combines everything into one complete mod. You remove both original mods and just use the merged one. This doesn't work for mods that use BG3 Script Extender though.

I'll go with "Patch" for this example since it's simpler. When you click either button, you'll see the mod metadata dialog:

![](https://raw.githubusercontent.com/0x1amy0urdad/Guidance/refs/heads/main/images/guidance-pic4.png)

For patches, it auto-generates a new UUID and fills in some defaults. For merges, it copies everything from your top priority mod (including the UUID—which means the in-game mod manager might try to re-download the original and overwrite your merged version, so heads up!).

A couple of checkboxes to know about:
- "Put the patch into the mods folder" tries to auto-install. It's hit or miss, so I'd recommend installing manually with [Laughing Leader's BG3 Mod Manager](https://github.com/LaughingLeader/BG3ModManager/releases) instead.
- "Re-use metadata from the top priority mod" does exactly what it says.

Click "OK" when you're ready.

### Step 6: Wait a moment

Grab another sip of that coffee while Guidance does its thing.

![](https://raw.githubusercontent.com/0x1amy0urdad/Guidance/refs/heads/main/images/guidance-pic5.png)

### Step 7: You're done!

If everything worked, you'll see this happy message:

![](https://raw.githubusercontent.com/0x1amy0urdad/Guidance/refs/heads/main/images/guidance-pic6.png)

Click "OK" and Guidance will open two folders in Windows Explorer:

![](https://raw.githubusercontent.com/0x1amy0urdad/Guidance/refs/heads/main/images/guidance-pic7.png)

The first is your BG3 Mods folder.

![](https://raw.githubusercontent.com/0x1amy0urdad/Guidance/refs/heads/main/images/guidance-pic8.png)

The second is where your new patch lives.

Just drag and drop the new .pak file into your Mods folder, then use LL's BG3 Mod Manager to set your load order (remember, the patch goes below the original mods). And you're all set!

## Under the hood

For the curious: Guidance is written in Python and packaged into an exe using [PyInstaller](https://pyinstaller.org/en/stable/).

The conflict resolution works by treating dialogs as directional graphs—each node is a question, answer, animation, or transition. My algorithm compares the two graphs and builds a new one that's essentially a union of both. It's not perfect yet (I'm still ironing out some edge cases), but it's getting there. The code's all on GitHub if you want to dive deeper.

## Need help?

The best way to reach me is through [this Discord server](https://discord.gg/reallyshadowheart)—just ping me in the `#mod-help` channel and I'll help you out!
