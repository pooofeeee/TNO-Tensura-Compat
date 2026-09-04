package com.tno.tensuracompat.core.endgame;

import com.tno.tensuracompat.core.stage.GearStageClasses;
import com.tno.tensuracompat.core.stage.ProductionStageScaling;
import com.tno.tensuracompat.core.stage.ScalableFamily;
import com.tno.tensuracompat.core.stage.Stage;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Optional;

/** Transient context for one synchronous, already-admitted native Magic/Holy damage event. */
public final class MagicHolyEndgameContext {
    private static final ThreadLocal<Deque<Frame>> FRAMES = ThreadLocal.withInitial(ArrayDeque::new);

    private MagicHolyEndgameContext() {
    }

    public static Optional<Scope> open(ItemStack gear, ScalableFamily family, LivingEntity target) {
        if (gear == null || gear.isEmpty() || !MagicHolyEndgamePolicy.supports(family)) {
            return Optional.empty();
        }
        if (GearStageClasses.classification(gear).isEmpty()) return Optional.empty();
        Optional<Stage> stage = ProductionStageScaling.stage(gear);
        if (stage.isEmpty()) return Optional.empty();
        MagicHolyEndgamePolicy.Parameters parameters = MagicHolyEndgamePolicy.parameters(stage.get(), family);
        if (!parameters.active()) return Optional.empty();
        Optional<L2HostilityTargetAdapter.TargetView> targetView =
                L2HostilityTargetAdapter.existingInitialized(target);
        if (targetView.isEmpty()) return Optional.empty();

        Frame frame = new Frame(stage.get(), family, target, targetView.get(), parameters);
        Deque<Frame> stack = FRAMES.get();
        stack.push(frame);
        return Optional.of(new Scope(Thread.currentThread(), frame));
    }

    static Optional<Frame> current() {
        Deque<Frame> stack = FRAMES.get();
        return stack.isEmpty() ? Optional.empty() : Optional.of(stack.peek());
    }

    record Frame(
            Stage stage,
            ScalableFamily family,
            LivingEntity target,
            L2HostilityTargetAdapter.TargetView l2Target,
            MagicHolyEndgamePolicy.Parameters parameters
    ) {
    }

    public static final class Scope implements AutoCloseable {
        private final Thread owner;
        private final Frame frame;
        private boolean closed;

        private Scope(Thread owner, Frame frame) {
            this.owner = owner;
            this.frame = frame;
        }

        @Override
        public void close() {
            if (closed) return;
            if (Thread.currentThread() != owner) {
                throw new IllegalStateException("endgame context closed on another thread");
            }
            Deque<Frame> stack = FRAMES.get();
            if (stack.isEmpty() || stack.pop() != frame) {
                throw new IllegalStateException("endgame context scope order violation");
            }
            if (stack.isEmpty()) FRAMES.remove();
            closed = true;
        }
    }
}
