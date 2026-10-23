# Chunks3

Cubic chunks for NeoForge 1.21.1. Chunks3 is a library mod: it lets another mod make its dimensions
keep their blocks in 16-block cubes from Y -16,384 to 16,383, with vanilla gameplay working on top
(mining, building, light, mobs, redstone, structures, portals) and its own distant terrain renderer.
It adds nothing to the game by itself.

It is the engine of [Earth Platform](https://github.com/pirut/earth-platform), split out so other
mods can build on it. It is early: the API below can still change between alpha versions.

## Using it

1. Depend on it (NeoForge `mods.toml` dependency on `chunks3`, and the jar on your build's classpath,
   or bundled jar-in-jar).
2. Add a dimension whose dimension type is a 16-block "carrier": `min_y` 0, `height` 16,
   `logical_height` 16. Vanilla chunks still exist there, empty; the blocks live in cubes.
3. Register it once, from your mod's constructor, with the generator its cubes come from:

```java
Cubic.register(MY_LEVEL, (level, folder) -> new MyGenerator(level.getSeed()));
```

A generator implements `io.github.pirut.chunks3.gen.CubeGenerator`. The required part is small:
`generate` (one 16³ cube), `surfaceY`, `farColumn` (the distant terrain at a level of detail) and
`seaLevel`. Everything else (structures, biome lookup, data prefetching, landing spots) has a default.
`gen.SurfaceGenerator` and `gen.HighlandsGenerator` show a complete heightmap world with caves, ores,
trees and vanilla structures.

The rest of the API:

| Call | What it does |
|---|---|
| `Cubic.register(key, generators)` | Makes a dimension cubic. The first one registered is the "home" that vanilla's Nether and End portals lead back to |
| `CubicDimension.cloudHeight(...)` | Where shader packs' clouds float in that dimension |
| `Cubic.addTransit(test)` | Entities passing far above the terrain (a jet stream, a fast flight) get no cubes loaded around them |
| `CubicLevel.of(level)` | The level's `CubeWorld` (null for vanilla levels): read and write blocks and light; on the server a `ServerCubeWorld`, with `loadAround` to make the cubes about a spot now |
| `CubicEvents.arriveWhenReady(...)` | Moves a player to a column once its cubes are made, landing on the ground; `CubicArrivalEvent` follows |
| `/cubes enter`, `where`, `status`, `light`, `find`, `locate` | Debug commands |

## Compatibility

Sodium, Iris (with shader packs that support Voxy-style far terrain, such as Photon), Lithium (Chunks3
turns off the Lithium features that read chunk sections directly), and many content mods: Create,
Mekanism, AE2, Waystones, Xaero's maps, JourneyMap, Chunky, Cobblemon, Twilight Forest, the Aether,
Sable. Distant Horizons is paused in cubic dimensions, since Chunks3 draws its own distant terrain.

## Building

Java 21. The far renderer compiles against Iris and Sodium, which are never bundled; supply the
tested jars:

```
export CHUNKS3_IRIS_JAR=/path/to/iris-neoforge-1.8.14-beta.1+mc1.21.1.jar
export CHUNKS3_SODIUM_JAR=/path/to/sodium-neoforge-0.8.12-beta.1+mc1.21.1.jar
LC_ALL=C.UTF-8 ./gradlew build
```

The `.github/workflows/ci.yml` file downloads both from Modrinth and checks their SHA-256.

Until Earth Platform depends on this library, the engine is still developed in Earth Platform's tree.
`tools/import_from_earth.py` copies it over: `python3 tools/import_from_earth.py ../earth-platform`.

Developer flags are `-Dchunks3.*` system properties (for example `-Dchunks3.far.fade=false`); they are
listed in Earth Platform's `docs/FLAGS.md`, where they are spelled `earthplatform.*`.

## License

LGPL-3.0-only (see `LICENSE` and `COPYING`). Mods of any license may depend on Chunks3; changes to
Chunks3 itself stay under the LGPL. The far terrain renderer is built on ideas from Voxy (Cortex) and
Distant Horizons (James Seibel and contributors) and contains no code from either.
