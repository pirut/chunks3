package io.github.pirut.chunks3;

import net.neoforged.fml.common.Mod;

/**
 * The NeoForge entry point. Chunks3 adds nothing by itself: a mod makes its dimensions cubic with
 * {@link Cubic#register}. Everything else registers itself through {@code @EventBusSubscriber}
 * classes and the mixins in {@code chunks3.mixins.json}.
 */
@Mod(Cubic.MOD_ID)
public final class Chunks3Mod {
    public Chunks3Mod() {
        Cubic.LOGGER.info("Chunks3 loaded");
    }
}
