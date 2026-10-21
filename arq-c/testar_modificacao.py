"""Checagem da modificação: com gamma=0 o modelo modificado é idêntico ao oficial; com gamma!=0, difere."""
import importlib.util, sys, types, torch

def carregar(pasta):
    for m in [m for m in sys.modules if m in ("models", "layers") or m.startswith(("models.", "layers."))]:
        del sys.modules[m]
    sys.path.insert(0, pasta)
    spec = importlib.util.spec_from_file_location("mt", f"{pasta}/models/ModernTCN.py"); mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod); sys.path.pop(0); return mod

cfg = types.SimpleNamespace(stem_ratio=6, downsample_ratio=2, ffn_ratio=1, num_blocks=[1], large_size=[51], small_size=[5],
    dims=[64] * 4, dw_dims=[64] * 4, enc_in=7, small_kernel_merged=False, dropout=0.3, head_dropout=0.0, use_multi_scale=False,
    revin=1, affine=0, subtract_last=0, freq="h", seq_len=336, individual=0, pred_len=96, kernel_size=25, patch_size=8,
    patch_stride=4, decomposition=0, use_attn=0)
torch.manual_seed(0)
oficial = carregar("moderntcn_oficial").Model(cfg).eval()
cfg.use_attn = 1
mod = carregar("moderntcn_mod").Model(cfg).eval()
falt = mod.load_state_dict(oficial.state_dict(), strict=False)
assert all("patch_attn" in k for k in falt.missing_keys) and not falt.unexpected_keys, falt
x = torch.randn(4, 336, 7)
with torch.no_grad():
    y0, y1 = oficial(x), mod(x)
assert y0.shape == y1.shape == (4, 96, 7)
assert torch.allclose(y0, y1, atol=1e-6), "gamma=0 deveria reproduzir o oficial"
mod.model.stages[0].blocks[0].patch_attn.gamma.data.fill_(1.0)
with torch.no_grad():
    assert not torch.allclose(y0, mod(x), atol=1e-4), "com gamma=1 a atenção deveria mudar a saída"
n = lambda m: sum(p.numel() for p in m.parameters())
print(f"ok | parâmetros: oficial {n(oficial):,} | modificado {n(mod):,} (+{n(mod)-n(oficial):,})")
