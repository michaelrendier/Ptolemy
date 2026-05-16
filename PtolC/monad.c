/*
 * PtolC/monad.c — C Monad: H_hat_RB field engine.
 *
 * learn()  deepens the beta field.
 * hear()   projects text onto the zero basis (internal, called by speak).
 * speak()  computes J^mu (Noether current) and returns ordered words.
 *
 * verbose levels:
 *   0 — silent
 *   1 — show mathematics (β deepening, J^μ propagation)
 *   2 — level 1 + ANSI colour (hear=cyan, speak=green, learn=yellow)
 *   3 — full pipeline: learn + hear + speak all shown simultaneously
 */

#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <stdio.h>
#include <unistd.h>

#include "ptolemy.h"
#include "monad.h"
#include "tokenizer.h"

/* Global colour enable — set by main() after isatty() check. */
int g_color = 0;

static const char *CY(void)  { return g_color ? C_YELLOW  : ""; }
static const char *CC(void)  { return g_color ? C_CYAN    : ""; }
static const char *CG(void)  { return g_color ? C_GREEN   : ""; }
static const char *CM(void)  { return g_color ? C_MAGENTA : ""; }
static const char *CB(void)  { return g_color ? C_BOLD    : ""; }
static const char *CR(void)  { return g_color ? C_RESET   : ""; }

/* ── Riemann zero generation (mirrors monad.py _generate_zeros) ───────────── */

static const double _EXACT_ZEROS[20] = {
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
};

static void generate_zeros(double *z, int N)
{
    int m = (N < 20) ? N : 20;
    for (int i = 0; i < m; i++) z[i] = _EXACT_ZEROS[i];
    if (N <= 20) return;

    double two_pi = 2.0 * M_PI;
    for (int n = 21; n <= N; n++) {
        double t = z[n-2] + (z[n-2] - z[n-3]);
        for (int iter = 0; iter < 30; iter++) {
            if (t < 2.0) t = (double)n * 3.0;
            double nt  = (t / two_pi) * (log(t / two_pi) - 1.0) + 0.875;
            double dnt = log(t / two_pi) / two_pi;
            if (fabs(dnt) < 1e-15) break;
            double dt  = (nt - n) / dnt;
            t -= dt;
            if (fabs(dt) < 1e-4) break;
        }
        z[n-1] = t;
    }
}

/* ── Word addressing (mirrors monad.py _word_coords) ─────────────────────── */

void monad_word_coords(const char *surface, int N, int *idx, double *E)
{
    uint64_t v = 0;
    for (const char *p = surface; *p; p++) {
        unsigned char c = (unsigned char)*p;
        int ci = (c >= 32 && c < 127) ? (int)(c - 32 + 1) : 0;
        v = v * 95ULL + (uint64_t)ci;
    }
    if (v > 0) v--;

    double seed = fmod((double)v * MONAD_PHI, 1.0);
    if (seed < 0.0) seed += 1.0;

    *idx = (int)(seed * N);
    if (*idx >= N) *idx = N - 1;
    if (*idx < 0)  *idx = 0;

    *E = MONAD_D_STAR + seed * (MONAD_OMEGA_ZS - MONAD_D_STAR);
}

/* ── FNV-1a hash ──────────────────────────────────────────────────────────── */

static uint32_t fnv1a(const char *s)
{
    uint32_t h = 2166136261u;
    while (*s) { h ^= (uint8_t)*s++; h *= 16777619u; }
    return h;
}

/* ── Word map ────────────────────────────────────────────────────────────── */

int monad_wm_get(const Monad *m, const char *word, int *idx, double *E)
{
    uint32_t h    = fnv1a(word);
    uint32_t mask = (uint32_t)(m->wm_cap - 1);
    uint32_t slot = h & mask;
    for (int i = 0; i < m->wm_cap; i++) {
        WMSlot *s = &m->wm[slot];
        if (!s->key) break;
        if (strcmp(s->key, word) == 0) {
            int dummy;
            monad_word_coords(word, m->N, &dummy, E);
            *idx = (int)s->idx;
            return 1;
        }
        slot = (slot + 1) & mask;
    }
    monad_word_coords(word, m->N, idx, E);
    return 0;
}

void monad_wm_set(Monad *m, const char *word, uint32_t idx)
{
    if (m->wm_size * 100 >= m->wm_cap * 65) {
        int      new_cap = m->wm_cap * 2;
        WMSlot  *new_wm  = calloc(new_cap, sizeof(WMSlot));
        uint32_t mask    = (uint32_t)(new_cap - 1);
        for (int i = 0; i < m->wm_cap; i++) {
            if (!m->wm[i].key) continue;
            uint32_t h = fnv1a(m->wm[i].key);
            uint32_t s = h & mask;
            while (new_wm[s].key) s = (s + 1) & mask;
            new_wm[s] = m->wm[i];
        }
        free(m->wm);
        m->wm     = new_wm;
        m->wm_cap = new_cap;
    }

    uint32_t h    = fnv1a(word);
    uint32_t mask = (uint32_t)(m->wm_cap - 1);
    uint32_t slot = h & mask;
    for (int i = 0; i < m->wm_cap; i++) {
        WMSlot *s = &m->wm[slot];
        if (!s->key) {
            s->key = strdup(word);
            s->idx = idx;
            m->wm_size++;
            return;
        }
        if (strcmp(s->key, word) == 0) { s->idx = idx; return; }
        slot = (slot + 1) & mask;
    }
}

/* ── A matrix ────────────────────────────────────────────────────────────── */

static uint32_t a_key(int i, int j)
{
    if (i > j) { int t = i; i = j; j = t; }
    return ((uint32_t)i << 15) | (uint32_t)j;
}

void monad_a_add(Monad *m, int i, int j, double delta)
{
    if (i == j) return;
    uint32_t key = a_key(i, j);
    if (key == 0) return;

    if (m->am_size * 100 >= m->am_cap * 65) {
        int    new_cap = m->am_cap * 2;
        ASlot *new_am  = calloc(new_cap, sizeof(ASlot));
        uint32_t mask  = (uint32_t)(new_cap - 1);
        for (int k = 0; k < m->am_cap; k++) {
            if (m->am[k].key == 0) continue;
            uint32_t s = m->am[k].key & mask;
            while (new_am[s].key) s = (s + 1) & mask;
            new_am[s] = m->am[k];
        }
        free(m->am);
        m->am     = new_am;
        m->am_cap = new_cap;
    }

    uint32_t mask = (uint32_t)(m->am_cap - 1);
    uint32_t slot = key & mask;
    for (int k = 0; k < m->am_cap; k++) {
        ASlot *s = &m->am[slot];
        if (s->key == 0) { s->key = key; s->val = delta; m->am_size++; return; }
        if (s->key == key) { s->val += delta; return; }
        slot = (slot + 1) & mask;
    }
}

double monad_a_get(const Monad *m, int i, int j)
{
    uint32_t key  = a_key(i, j);
    uint32_t mask = (uint32_t)(m->am_cap - 1);
    uint32_t slot = key & mask;
    for (int k = 0; k < m->am_cap; k++) {
        ASlot *s = &m->am[slot];
        if (s->key == 0) return 0.0;
        if (s->key == key) return s->val;
        slot = (slot + 1) & mask;
    }
    return 0.0;
}

/* ── Lifecycle ────────────────────────────────────────────────────────────── */

Monad *monad_create(int N)
{
    Monad *m = calloc(1, sizeof(Monad));
    m->N                  = N;
    m->ground             = fabs(MONAD_L_GROUND) / N;
    m->emission_threshold = fabs(MONAD_L_GROUND) * 2.0;

    m->zeros = malloc(N * sizeof(double));
    m->beta  = malloc(N * sizeof(double));
    m->age   = calloc(N, sizeof(int));
    m->vocab = calloc(N, sizeof(VocabEntry));

    m->wm_cap = 65536;
    m->wm     = calloc(m->wm_cap, sizeof(WMSlot));
    m->am_cap = 131072;
    m->am     = calloc(m->am_cap, sizeof(ASlot));

    return m;
}

void monad_destroy(Monad *m)
{
    if (!m) return;
    free(m->zeros); free(m->beta); free(m->age); free(m->vocab);
    for (int i = 0; i < m->wm_cap; i++) if (m->wm[i].key) free(m->wm[i].key);
    free(m->wm); free(m->am); free(m);
}

void monad_ground_init(Monad *m)
{
    generate_zeros(m->zeros, m->N);
    for (int i = 0; i < m->N; i++) { m->beta[i] = m->ground; m->age[i] = 0; }
}

/* ── learn() ──────────────────────────────────────────────────────────────── */

void monad_learn(Monad *m, const char *text, int verbose)
{
    const char *p   = text;
    int         len = strlen(text);
    char       *sbuf = malloc(len + 2);

    while (*p) {
        int slen = 0;
        while (*p && *p != '.' && *p != '!' && *p != '?' && *p != '\n')
            sbuf[slen++] = *p++;
        if (*p) p++;
        sbuf[slen] = '\0';
        if (slen < 2) continue;

        int    ntok = 0;
        char **toks = tok_split(sbuf, &ntok);
        if (ntok == 0) { tok_free(toks, ntok); continue; }

        int    *sidx     = malloc(ntok * sizeof(int));
        double *sE       = malloc(ntok * sizeof(double));
        double *old_beta = malloc(ntok * sizeof(double));
        int     nact     = 0;

        for (int t = 0; t < ntok; t++) {
            const char *word = toks[t];
            int idx; double E;
            monad_wm_get(m, word, &idx, &E);
            monad_wm_set(m, word, (uint32_t)idx);

            old_beta[nact] = m->beta[idx];

            double nb = m->beta[idx] + E * MONAD_ALPHA_LEARN;
            if (nb > MONAD_BETA_SAT) nb = MONAD_BETA_SAT;
            m->beta[idx] = nb;

            if (!m->vocab[idx].present || E > m->vocab[idx].E) {
                strncpy(m->vocab[idx].word, word, MAX_WORD_LEN - 1);
                m->vocab[idx].word[MAX_WORD_LEN - 1] = '\0';
                m->vocab[idx].E       = E;
                m->vocab[idx].present = 1;
            }

            sidx[nact] = idx; sE[nact] = E; nact++;
            m->word_count++;
        }

        /* ── Verbose: learn output ───────────────────────────────────────── */
        if (verbose >= 1) {
            fprintf(stderr, "%s%s[learn]%s ",
                    CB(), CY(), CR());
            if (slen > 72)
                fprintf(stderr, "\"%.*s...\"\n", 72, sbuf);
            else
                fprintf(stderr, "\"%s\"\n", sbuf);

            for (int t = 0; t < nact; t++) {
                double delta = m->beta[sidx[t]] - old_beta[t];
                fprintf(stderr,
                    "  %s%-18s%s z#%-6d  γ=%s%-11.3f%s  E=%s%.4f%s"
                    "  β: %.6f → %.6f  %sΔβ=+%.6f%s\n",
                    CB(), toks[t], CR(),
                    sidx[t],
                    CB(), m->zeros[sidx[t]], CR(),
                    CB(), sE[t], CR(),
                    old_beta[t], m->beta[sidx[t]],
                    CY(), delta, CR());
            }
        }

        /* Gauge connections */
        for (int i = 0; i < nact; i++) {
            for (int j = i + 1; j < nact; j++) {
                if (sidx[i] == sidx[j]) continue;
                double dist = fabs(m->zeros[sidx[i]] - m->zeros[sidx[j]]);
                if (dist < 1e-4) dist = 1e-4;
                double w = sE[i] * sE[j] / dist;

                if (verbose >= 1) {
                    fprintf(stderr,
                        "  %sA%s[%d↔%d] +=%s %.4e%s"
                        "  (|Δγ|=%s%.2f%s  E_i·E_j=%s%.4f%s)\n",
                        CM(), CR(), sidx[i], sidx[j],
                        CY(), w, CR(),
                        CB(), dist, CR(),
                        CB(), sE[i]*sE[j], CR());
                }

                monad_a_add(m, sidx[i], sidx[j], w);
            }
        }

        free(sidx); free(sE); free(old_beta);
        tok_free(toks, ntok);
    }

    free(sbuf);
}

/* ── hear() (internal) ────────────────────────────────────────────────────── */

typedef struct { int idx; double E; } Activation;

static Activation *monad_hear_raw(Monad *m, const char *query, int *n_out,
                                   int verbose)
{
    int    ntok = 0;
    char **toks = tok_split(query, &ntok);
    Activation *act = malloc((ntok + 1) * sizeof(Activation));
    *n_out = 0;

    if (verbose >= 1 && ntok > 0)
        fprintf(stderr, "%s%s[hear]%s  \"%s\"\n", CB(), CC(), CR(), query);

    for (int t = 0; t < ntok; t++) {
        int idx; double E;
        monad_wm_get(m, toks[t], &idx, &E);

        double beta = m->beta[idx];
        double w    = exp(-MONAD_LAMBDA * m->age[idx]);
        double Jp   = beta * E * E * w;

        if (verbose >= 1) {
            int known = monad_wm_get(m, toks[t], &idx, &E);
            fprintf(stderr,
                "  %s%-18s%s z#%-6d  γ=%s%-11.3f%s  σ=%s0.5%s"
                "  E=%s%.4f%s  β=%s%.6f%s  w=%s%.4f%s"
                "  %sJ_p=%.4f%s  %s\n",
                CB(), toks[t], CR(),
                idx,
                CB(), m->zeros[idx], CR(),
                CB(), CR(),
                CB(), E, CR(),
                CC(), beta, CR(),
                CB(), w, CR(),
                CM(), Jp, CR(),
                known ? "" : "[new]");
        }

        act[(*n_out)].idx = idx;
        act[(*n_out)].E   = E;
        (*n_out)++;
    }

    tok_free(toks, ntok);
    return act;
}

/* ── speak() ──────────────────────────────────────────────────────────────── */

typedef struct { int idx; double J; } JEntry;
static int jcmp(const void *a, const void *b)
{
    double da = ((JEntry *)a)->J;
    double db = ((JEntry *)b)->J;
    return (da < db) ? 1 : (da > db) ? -1 : 0;
}

/* Top-N A propagation contributions for verbose display */
#define VPROP_MAX 8
typedef struct { int from, to; double contrib; } VProp;
static int vpcmp(const void *a, const void *b)
{
    double da = ((VProp *)a)->contrib;
    double db = ((VProp *)b)->contrib;
    return (da < db) ? 1 : (da > db) ? -1 : 0;
}

char *monad_speak(Monad *m, const char *query, int max_tokens, int verbose)
{
    int n_act = 0;
    Activation *psi;

    if (query && query[0]) {
        psi = monad_hear_raw(m, query, &n_act, verbose);
    } else {
        /* Spontaneous emission */
        int cap = m->N < 200 ? m->N : 200;
        psi = malloc(cap * sizeof(Activation));
        for (int i = 0; i < cap; i++) {
            psi[i].idx = i;
            psi[i].E   = m->vocab[i].present ? m->vocab[i].E : MONAD_D_STAR;
        }
        n_act = cap;
        if (verbose >= 1)
            fprintf(stderr, "%s%s[speak]%s spontaneous emission\n",
                    CB(), CG(), CR());
    }

    /* Dense J field */
    double *J = malloc((size_t)m->N * sizeof(double));
    memset(J, 0, (size_t)m->N * sizeof(double));

    /* Primary: J[idx] = beta[idx] * E^2 * recency */
    for (int k = 0; k < n_act; k++) {
        int    idx = psi[k].idx;
        double E   = psi[k].E;
        double w   = exp(-MONAD_LAMBDA * m->age[idx]);
        J[idx] += m->beta[idx] * E * E * w;
    }

    /* Propagate through A with verbose collection */
    VProp vprop[VPROP_MAX];
    int   nvp = 0;
    double min_vp = 0.0;

    for (int k = 0; k < m->am_cap; k++) {
        if (m->am[k].key == 0) continue;
        int    i   = (int)(m->am[k].key >> 15);
        int    j   = (int)(m->am[k].key & 0x7FFF);
        double aw  = m->am[k].val;
        double wi  = exp(-MONAD_LAMBDA * m->age[i]);
        double wj  = exp(-MONAD_LAMBDA * m->age[j]);

        if (J[i] > 0.0) {
            double contrib = J[i] * aw * m->beta[j] * wj;
            J[j] += contrib;
            if (verbose >= 1 && contrib > min_vp) {
                if (nvp < VPROP_MAX) {
                    vprop[nvp++] = (VProp){i, j, contrib};
                } else {
                    /* Replace smallest */
                    int mi = 0;
                    for (int x = 1; x < VPROP_MAX; x++)
                        if (vprop[x].contrib < vprop[mi].contrib) mi = x;
                    if (contrib > vprop[mi].contrib)
                        vprop[mi] = (VProp){i, j, contrib};
                    min_vp = vprop[mi].contrib;
                }
            }
        }
        if (J[j] > 0.0) {
            double contrib = J[j] * aw * m->beta[i] * wi;
            J[i] += contrib;
        }
    }

    /* Verbose: J^mu propagation */
    if (verbose >= 1 && nvp > 0) {
        qsort(vprop, nvp, sizeof(VProp), vpcmp);
        fprintf(stderr, "%s%s[J^μ propagation — top %d]%s\n",
                CB(), CM(), nvp, CR());
        for (int k = 0; k < nvp; k++) {
            int fi = vprop[k].from, ti = vprop[k].to;
            const char *fw = m->vocab[fi].present ? m->vocab[fi].word : "?";
            const char *tw = m->vocab[ti].present ? m->vocab[ti].word : "?";
            fprintf(stderr,
                "  z#%d(%s%s%s) → z#%d(%s%s%s)"
                "  contrib=%s%.4e%s"
                "  A=%.4e  β[%d]=%.4f\n",
                fi, CB(), fw, CR(),
                ti, CB(), tw, CR(),
                CM(), vprop[k].contrib, CR(),
                monad_a_get(m, fi, ti), ti, m->beta[ti]);
        }
    }

    /* Collect and sort (idx, J) pairs with vocab entries */
    int     njv = 0;
    JEntry *jv  = malloc((size_t)m->N * sizeof(JEntry));
    for (int i = 0; i < m->N; i++) {
        if (J[i] > 0.0 && m->vocab[i].present) {
            jv[njv].idx = i; jv[njv].J = J[i]; njv++;
        }
    }
    qsort(jv, njv, sizeof(JEntry), jcmp);

    /* Verbose: ranking */
    if (verbose >= 1 && njv > 0) {
        int show = njv < 12 ? njv : 12;
        fprintf(stderr, "%s%s[ranking — top %d]%s\n", CB(), CG(), show, CR());
        for (int k = 0; k < show; k++) {
            fprintf(stderr, "  %2d. %s%-18s%s z#%-6d  J=%s%.4e%s\n",
                    k+1,
                    CB(), m->vocab[jv[k].idx].word, CR(),
                    jv[k].idx,
                    CG(), jv[k].J, CR());
        }
    }

    /* Build response string */
    int   out_cap = max_tokens * (MAX_WORD_LEN + 1) + 4;
    char *out     = malloc(out_cap);
    out[0] = '\0';
    int written = 0;
    for (int i = 0; i < njv && written < max_tokens; i++) {
        const char *w = m->vocab[jv[i].idx].word;
        if (out[0]) strncat(out, " ", out_cap - strlen(out) - 1);
        strncat(out, w, out_cap - strlen(out) - 1);
        written++;
    }

    /* Advance age */
    for (int i = 0; i < m->N; i++) m->age[i]++;
    for (int k = 0; k < n_act; k++) m->age[psi[k].idx] = 0;

    free(J); free(jv); free(psi);
    return out;
}

/* ── Diagnostics ──────────────────────────────────────────────────────────── */

void monad_status(const Monad *m, FILE *out)
{
    int vocab_count = 0;
    double deepest = 0.0; int deepest_idx = 0;
    for (int i = 0; i < m->N; i++) {
        if (m->vocab[i].present) vocab_count++;
        if (m->beta[i] > deepest) { deepest = m->beta[i]; deepest_idx = i; }
    }
    fprintf(out,
        "[monad] N=%d  vocab=%d  A_edges=%d  word_count=%d\n"
        "        ground=%.8f  deepest_β=%.4f (z#%d  γ=%.4f  \"%s\")\n"
        "        σ=0.5 (Noether forcing)  wm=%d/%d  am=%d/%d\n",
        m->N, vocab_count, m->am_size, m->word_count,
        m->ground, deepest, deepest_idx,
        (deepest_idx < m->N) ? m->zeros[deepest_idx] : 0.0,
        m->vocab[deepest_idx].present ? m->vocab[deepest_idx].word : "?",
        m->wm_size, m->wm_cap, m->am_size, m->am_cap);
}

void monad_lookup(const Monad *m, const char *word, FILE *out)
{
    int    idx; double E;
    int    known = monad_wm_get(m, word, &idx, &E);
    double beta  = m->beta[idx];
    double gamma = (idx < m->N) ? m->zeros[idx] : 0.0;
    fprintf(out,
        "  %-24s z#%-6d  γ=%-11.4f  σ=0.5  E=%.4f  β=%.6f  %s\n",
        word, idx, gamma, E, beta, known ? "[known]" : "[new]");
}
