"""Forward hook logic for hidden state extraction and injection.

Hooks are registered on specific transformer layers to intercept the residual
stream mid-forward-pass.  Neither model's weights nor architecture are modified.
"""

import torch
import torch.nn as nn
from typing import Optional, Literal


class HiddenStateCapture:
    """Captures the output hidden state of a transformer layer via a forward hook.

    After the hooked layer runs, ``self.captured`` holds the hidden state tensor.
    The tensor is *not* cloned by default — it shares memory with the model's
    activations.  Call ``.clone()`` on it if you need it to survive past the
    current forward pass.
    """

    def __init__(self):
        self.captured: Optional[torch.Tensor] = None
        self._handle: Optional[torch.utils.hooks.RemovableHook] = None

    def hook_fn(self, module: nn.Module, input, output):
        # Qwen2 decoder layers return a tuple: (hidden_states, ...).
        # We want the hidden_states tensor (element 0).
        if isinstance(output, tuple):
            self.captured = output[0]
        else:
            self.captured = output

    def register(self, module: nn.Module) -> "HiddenStateCapture":
        self._handle = module.register_forward_hook(self.hook_fn)
        return self

    def remove(self):
        if self._handle is not None:
            self._handle.remove()
            self._handle = None

    def get(self, clone: bool = True) -> torch.Tensor:
        assert self.captured is not None, "Hook has not fired yet"
        return self.captured.clone() if clone else self.captured


class HiddenStateInjector:
    """Injects a hidden state into the residual stream at a specific layer.

    Supports two modes:
      - "replace": fully overwrite the residual stream with the injected tensor.
      - "add": add the injected tensor to the existing residual stream.

    The injector is *armed* by calling ``set_state(tensor)`` before the forward
    pass.  After the hook fires once, it automatically disarms (to avoid leaking
    into subsequent forward passes).  Re-arm by calling ``set_state`` again.
    """

    def __init__(self, mode: Literal["add", "replace"] = "add"):
        self.mode = mode
        self._state: Optional[torch.Tensor] = None
        self._handle: Optional[torch.utils.hooks.RemovableHook] = None

    def hook_fn(self, module: nn.Module, input, output):
        if self._state is None:
            return output  # not armed — pass through

        if isinstance(output, tuple):
            hidden = output[0]
        else:
            hidden = output

        injected = self._state.to(hidden.dtype).to(hidden.device)

        # DESIGN DECISION: When sequence lengths don't match (e.g. injected
        # state is a single-token representation while the layer outputs a full
        # sequence), we inject at the *last* sequence position.  This aligns
        # with the causal LM convention where the last position carries the
        # most information for next-token prediction.
        if injected.shape[1] != hidden.shape[1]:
            if self.mode == "replace":
                hidden = hidden.clone()
                hidden[:, -injected.shape[1]:, :] = injected
            else:
                hidden = hidden.clone()
                hidden[:, -injected.shape[1]:, :] = hidden[:, -injected.shape[1]:, :] + injected
        else:
            if self.mode == "replace":
                hidden = injected
            else:
                hidden = hidden + injected

        # Disarm after one use
        self._state = None

        if isinstance(output, tuple):
            return (hidden,) + output[1:]
        return hidden

    def set_state(self, state: torch.Tensor):
        """Arm the injector with a hidden state for the next forward pass."""
        self._state = state

    def register(self, module: nn.Module) -> "HiddenStateInjector":
        self._handle = module.register_forward_hook(self.hook_fn)
        return self

    def remove(self):
        if self._handle is not None:
            self._handle.remove()
            self._handle = None


class NativeHiddenCapture:
    """Captures the large model's *own* hidden state at a target layer.

    Used to compute the hidden alignment loss: we need the large model's native
    representation at the injection layer for the same input, without any
    injection applied.  This is run on a separate forward pass (the "probe"
    pass).
    """

    def __init__(self):
        self.captured: Optional[torch.Tensor] = None
        self._handle: Optional[torch.utils.hooks.RemovableHook] = None

    def hook_fn(self, module, input, output):
        if isinstance(output, tuple):
            self.captured = output[0].detach().clone()
        else:
            self.captured = output.detach().clone()

    def register(self, module: nn.Module) -> "NativeHiddenCapture":
        self._handle = module.register_forward_hook(self.hook_fn)
        return self

    def remove(self):
        if self._handle is not None:
            self._handle.remove()
            self._handle = None

    def get(self) -> torch.Tensor:
        assert self.captured is not None, "Hook has not fired yet"
        return self.captured
