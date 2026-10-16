<?php

namespace app\logic;

/**
 * LatexSanitizer
 *
 * Dedicated service for LaTeX equation & prose sanitization, AST-level
 * algebraic canonicalization, commutative term normalization, and
 * fallback explanation synthesis.
 */
class LatexSanitizer
{
    /**
     * Sanitizes a raw equation string against HTML tags and formatting leaks.
     */
    public function sanitizeEquation(string $eq): string
    {
        $eq = preg_replace('/<(?:strong|b)>(.*?)<\/(?:strong|b)>/i', '\\mathbf{$1}', $eq);
        $eq = preg_replace('/<(?:em|i)>(.*?)<\/(?:em|i)>/i', '\\mathit{$1}', $eq);
        $eq = strip_tags($eq);
        return trim($eq);
    }

    /**
     * Sanitizes all formula prose fields against control character collisions,
     * normalizes inline math delimiters to canonical $ ... $ form, and strips
     * mechanical LLM boilerplate ("interpreted as follows:"), raw Markdown
     * bold (**...**), and raw Markdown bullet lists (\n* ...).
     */
    public function sanitizeProseFields(array $data): array
    {
        $proseFields = [
            'conceptual_definition',
            'intuitive_summary',
            'interpretation',
            'symmetry_origin',
            'limits_and_boundary',
            'description'
        ];

        foreach ($proseFields as $field) {
            if (!empty($data[$field]) && is_string($data[$field])) {
                $val = $data[$field];
                $val = str_replace(["\x08ar{", "\x08\\bar{", "ar{"], '\bar{', $val);
                $val = str_replace(["\x08eta", "\x08"], ['\beta', ''], $val);
                $val = str_replace(["\x0crac", "\x0c"], ['\frac', ''], $val);
                $val = preg_replace('/[\x00-\x08\x0b\x0c\x0e-\x1f]/', '', $val);

                // Clean double backslashes before standard LaTeX macros
                $val = preg_replace('/\\\\\\\\(mathcal|mathbf|oint|iint|frac|dot|ddot|vec|hat|bar|nabla|partial|sum|int|text|sigma|tau|mu|nu|rho|lambda)/', '\\\\$1', $val);

                // Clean stray escaped dollars
                $val = str_replace(['\\$', '\\ $'], '$', $val);

                // Canonicalize inline bracket delimiters \( ... \) to standard $ ... $
                $val = preg_replace('/\\\\\((.*?)\\\\\)/s', '$$1$', $val);

                // Fix misplaced equals or fraction delimiters
                $val = preg_replace('/=\$\s*\\\\frac/', '= \\frac', $val);
                $val = preg_replace('/is\$\s*\\\\frac/', 'is \\frac', $val);

                // Convert literal '\n' before numbered lists or bullet items to actual newlines
                $val = preg_replace('/\\\\n(?=\s*(?:\d+\.|\*|-))/u', "\n", $val);

                // Mask math blocks before prose artifact cleanup
                $mathBlocks = [];
                $masked = preg_replace_callback(
                    '/(\$\$[\s\S]*?\$\$|\\\\\[[\s\S]*?\\\\\]|(?<!\\\\)\$(?:[^$\\\\]|\\\\.)+?\$)/u',
                    function ($m) use (&$mathBlocks) {
                        $idx = count($mathBlocks);
                        $mathBlocks[] = $m[0];
                        return "__MATH_{$idx}__";
                    },
                    $val
                );

                // Strip raw Markdown bold **...** outside math blocks
                if (str_contains($masked, '**')) {
                    $masked = preg_replace('/\*\*([^*\n]+)\*\*/u', '$1', $masked);
                    $masked = str_replace('**', '', $masked);
                }

                // Strip mechanical "interpreted as follows:" boilerplate
                if (stripos($masked, 'interpreted as follows') !== false) {
                    $masked = preg_replace(
                        '/(?:^(?:(?:Mathematically|Physically|Specifically|Here),\s+)?(?:the|this|it)\s+(?:(?:\w+\s+){0,3})?(?:formula|equation|relation|expression|identity|statement|term|law|condition|form)?\s*(?:__MATH_\d+__\s*)?(?:is|can\s+be|may\s+be)\s+interpreted\s+as\s+follows\s*:\s*)|(?:(?:,\s*|\s+)(?:which\s+)?(?:is|can\s+be)\s+interpreted\s+as\s+follows\s*:\s*)|(?:interpreted\s+as\s+follows\s*:\s*)/iu',
                        ' ',
                        $masked
                    );
                    $masked = ltrim($masked, " \t\n\r\0\x0B.,;:");
                }

                // Convert raw Markdown bullet lists (\n* ... or ^* ...) into continuous prose sentences
                if (preg_match('/(?:^|\n)\s*[\*-]\s+/u', $masked)) {
                    $lines = explode("\n", $masked);
                    $parts = [];
                    foreach ($lines as $line) {
                        $s = trim($line);
                        if ($s === '') {
                            continue;
                        }
                        if (preg_match('/^[\*-]\s+(.*)$/u', $s, $bm)) {
                            $item = trim($bm[1]);
                            if ($item !== '' && !in_array( substr($item, -1), ['.', '!', '?'], true)) {
                                $item .= '.';
                            }
                            $parts[] = $item;
                        } else {
                            if (str_ends_with($s, ':')) {
                                $s = rtrim(substr($s, 0, -1)) . '.';
                            } elseif (!in_array(substr($s, -1), ['.', '!', '?'], true)) {
                                $s .= '.';
                            }
                            $parts[] = $s;
                        }
                    }
                    $masked = implode(' ', $parts);
                }

                $masked = trim(preg_replace('/ {2,}/', ' ', $masked));
                if ($masked !== '' && ctype_lower($masked[0])) {
                    $masked = strtoupper($masked[0]) . substr($masked, 1);
                }

                // Unmask math blocks
                $val = preg_replace_callback('/__MATH_(\d+)__/', function ($m) use ($mathBlocks) {
                    return $mathBlocks[(int)$m[1]] ?? $m[0];
                }, $masked);

                $data[$field] = trim($val);
            }
        }

        return $data;
    }

    /**
     * Sanitizes malformed TeX escape sequences in formula prose fields on read.
     */
    public function sanitizeFormulaText(array $formula): array
    {
        $fields = ['interpretation', 'limits_and_boundary', 'symmetry_origin', 'conceptual_definition', 'intuitive_summary'];
        foreach ($fields as $field) {
            if (!empty($formula[$field]) && is_string($formula[$field])) {
                $txt = $formula[$field];
                $txt = str_replace('\\backslash)', ')', $txt);
                $txt = str_replace('\\backslash', '\\', $txt);
                $formula[$field] = $txt;
            }
        }
        return $formula;
    }

    /**
     * Canonicalizes LaTeX mathematical strings to AST-level algebraic signatures.
     */
    public function canonicalizeLatex(string $latex): string
    {
        if (empty($latex)) {
            return '';
        }
        $clean = preg_replace('/\\\\par\b/', ' ', $latex);
        $clean = preg_replace('/\\\\left|\\\\right/', '', $clean);
        $clean = preg_replace('/\\\\quad|\\\\qquad|\\\\,/', ' ', $clean);
        $clean = preg_replace('/\\\\varepsilon(?![a-zA-Z])/', '\\epsilon', $clean);
        $clean = preg_replace('/\\\\vartheta(?![a-zA-Z])/', '\\theta', $clean);
        $clean = preg_replace('/\\\\varphi(?![a-zA-Z])/', '\\phi', $clean);
        $clean = preg_replace('/\\\\varrho(?![a-zA-Z])/', '\\rho', $clean);
        $clean = preg_replace('/\\\\varpi(?![a-zA-Z])/', '\\pi', $clean);
        $clean = preg_replace('/\\\\varsigma(?![a-zA-Z])/', '\\sigma', $clean);

        // Strip visual styling commands
        $clean = preg_replace('/\\\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\\{([^}]+)\\}/', '$2', $clean);
        $clean = preg_replace('/\\\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\\\[a-zA-Z]+|[a-zA-Z0-9])/', '$2', $clean);
        $hasHtml = true;
        while ($hasHtml) {
            $next = preg_replace('/\\\\(cssId|class|style|href)\\{[^{}]*\\}\\{((?:[^{}]|\\{[^{}]*\\})*)\\}/', '$2', $clean);
            if ($next === $clean) {
                $hasHtml = false;
            } else {
                $clean = $next;
            }
        }
        $clean = preg_replace('/\\\\(cssId|class|style|href)\b/', '', $clean);

        // Canonicalize fractions
        $hasFraction = true;
        while ($hasFraction) {
            $next = preg_replace('/\\\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/', '($1)/($2)', $clean);
            if ($next === $clean) {
                $hasFraction = false;
            } else {
                $clean = $next;
            }
        }

        // Canonicalize vector operators
        $clean = preg_replace('/\\\\nabla\s*\\\\times/', 'curl', $clean);
        $clean = preg_replace('/\\\\nabla\s*\\\\cdot/', 'div', $clean);
        $clean = preg_replace('/\\\\nabla\^2/', 'laplacian', $clean);
        $clean = preg_replace('/\\\\nabla/', 'grad', $clean);

        // Canonicalize limits: \to 0 -> =0
        $clean = preg_replace('/\\\\to\s*0/', '=0', $clean);
        $clean = preg_replace('/\\\\rightarrow\s*0/', '=0', $clean);

        // Strip whitespace and commas
        $clean = preg_replace('/\s+/', '', $clean);
        $clean = str_replace(',', '', $clean);
        return strtolower($clean);
    }

    /**
     * Normalizes LaTeX mathematical strings to ignore white spaces, styles, and braces.
     */
    public function normalizeLatex(string $latex): string
    {
        $normalized = $latex;
        $normalized = preg_replace('/\\\\varepsilon(?![a-zA-Z])/', '\\epsilon', $normalized);
        $normalized = preg_replace('/\\\\vartheta(?![a-zA-Z])/', '\\theta', $normalized);
        $normalized = preg_replace('/\\\\varphi(?![a-zA-Z])/', '\\phi', $normalized);
        $normalized = preg_replace('/\\\\varrho(?![a-zA-Z])/', '\\rho', $normalized);
        $normalized = preg_replace('/\\\\varpi(?![a-zA-Z])/', '\\pi', $normalized);
        $normalized = preg_replace('/\\\\varsigma(?![a-zA-Z])/', '\\sigma', $normalized);
        // Strip delimiters
        $normalized = preg_replace('/^\\\\\\(/', '', $normalized);
        $normalized = preg_replace('/\\\\\\)$/', '', $normalized);
        $normalized = preg_replace('/^\\\\\\[/', '', $normalized);
        $normalized = preg_replace('/\\\\\\]$/', '', $normalized);
        $normalized = preg_replace('/^\$\$/', '', $normalized);
        $normalized = preg_replace('/\$\$$/', '', $normalized);
        $normalized = preg_replace('/^\$/', '', $normalized);
        $normalized = preg_replace('/\$$/', '', $normalized);

        // Strip visual styling commands like \vec, \mathbf, \hat, \mathrm, \cssId
        $normalized = preg_replace('/\\\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\\{([^}]+)\\}/', '$2', $normalized);
        $normalized = preg_replace('/\\\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\\\[a-zA-Z]+|[a-zA-Z0-9])/', '$2', $normalized);

        // Strip MathJax HTML extension wraps (\class, \cssId, \style, \href) to compare only pure math
        $hasHtml = true;
        while ($hasHtml) {
            $next = preg_replace('/\\\\(cssId|class|style|href)\\{[^{}]*\\}\\{((?:[^{}]|\\{[^{}]*\\})*)\\}/', '$2', $normalized);
            if ($next === $normalized) {
                $hasHtml = false;
            } else {
                $normalized = $next;
            }
        }
        $normalized = preg_replace('/\\\\(cssId|class|style|href)\b/', '', $normalized);

        // Canonicalize LaTeX fraction commands: \frac{A}{B} -> A/B
        $hasFraction = true;
        while ($hasFraction) {
            $next = preg_replace('/\\\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/', '$1/$2', $normalized);
            if ($next === $normalized) {
                $hasFraction = false;
            } else {
                $normalized = $next;
            }
        }

        // Flatten braced subscripts for comparison: e.g. _{ext} -> _ext, _{GUT} -> _gut
        $normalized = preg_replace('/_\{([^}]+)\}/', '_$1', $normalized);

        // Strip whitespaces, backslashes, and braces
        $normalized = preg_replace('/[^a-zA-Z0-9_\\^\\-=+\\/*()\\[\\]<>\.,;?]/', '', $normalized);
        $normalized = strtolower($normalized);

        // Normalize algebraic structure (commutative sorting of products and sums)
        return $this->normalizeAlgebraicStructure($normalized);
    }

    private function sortTermFactors(string $term, array $multiSymbols): string
    {
        $temp = $term;
        $factors = [];

        // 1. Extract division blocks (e.g. /2)
        $pattern = '/\/(?:[0-9]+|dtau|dtheta|dphi|dchi|deta|domega|dlambda|dpsi|ds|dt|dx|dy|dz|dr|dp|dq|df|dg|dh|dk|epsilon|theta|phi|rho|pi|sigma|tau|int|oint|iint|iiint|partial|nabla|hbar|psi|lambda|omega|gamma|mu|nu|eta|delta|beta|alpha|chi|zeta|[a-zA-Z])/';
        $temp = preg_replace_callback($pattern, function ($matches) use (&$factors) {
            $factors[] = $matches[0];
            return '';
        }, $temp);

        // 2. Extract multi-character symbols (with optional exponents like ^2 or 2)
        foreach ($multiSymbols as $sym) {
            $regex = '/' . preg_quote($sym, '/') . '(?:_[a-zA-Z0-9]+)?(?:\^[0-9]+|[0-9]+)?/';
            $temp = preg_replace_callback($regex, function ($matches) use (&$factors) {
                $factors[] = $matches[0];
                return ' ';
            }, $temp);
        }

        // 3. Extract remaining single letters/variables with optional subscripts and exponents (e.g. e_gut, e^2, e2, c)
        $temp = preg_replace_callback('/[a-zA-Z](?:_[a-zA-Z0-9]+)?(?:\^[0-9]+|[0-9]+)?/', function ($matches) use (&$factors) {
            $factors[] = $matches[0];
            return ' ';
        }, $temp);

        // 4. Extract any remaining numbers
        $temp = preg_replace_callback('/[0-9]+/', function ($matches) use (&$factors) {
            $factors[] = $matches[0];
            return ' ';
        }, $temp);

        sort($factors);
        return implode('', $factors);
    }

    private function normalizeAlgebraicStructure(string $latex): string
    {
        $parts = explode('=', $latex);
        $normalizedParts = [];

        $multiSymbols = [
            'dtau', 'dtheta', 'dphi', 'dchi', 'deta', 'domega', 'dlambda', 'dpsi', 'ds', 'dt', 'dx', 'dy', 'dz', 'dr', 'dp', 'dq', 'df', 'dg', 'dh', 'dk',
            'epsilon', 'theta', 'phi', 'rho', 'pi', 'sigma', 'tau', 'int', 'oint', 'iint', 'iiint',
            'partial', 'nabla', 'hbar', 'psi', 'lambda', 'omega', 'gamma', 'mu', 'nu', 'eta', 'delta',
            'beta', 'alpha', 'chi', 'zeta'
        ];

        foreach ($parts as $part) {
            $tokens = preg_split('/([+\-])/', $part, -1, PREG_SPLIT_DELIM_CAPTURE | PREG_SPLIT_NO_EMPTY);

            $currentSign = '+';
            $terms = [];

            foreach ($tokens as $tok) {
                if ($tok === '+' || $tok === '-') {
                    $currentSign = $tok;
                } else {
                    $sortedTerm = $this->sortTermFactors($tok, $multiSymbols);
                    if (!empty($sortedTerm)) {
                        $terms[] = [
                            'sign' => $currentSign,
                            'term' => $sortedTerm
                        ];
                    }
                    $currentSign = '+';
                }
            }

            usort($terms, function ($a, $b) {
                return strcmp($a['term'], $b['term']);
            });

            $joined = '';
            foreach ($terms as $i => $t) {
                if ($i === 0) {
                    if ($t['sign'] === '-') {
                        $joined .= '-';
                    }
                    $joined .= $t['term'];
                } else {
                    $joined .= $t['sign'] . $t['term'];
                }
            }
            $normalizedParts[] = $joined;
        }

        return implode('=', $normalizedParts);
    }

    /**
     * Synthesizes a structured formula explanation dynamically from LaTeX AST parsing
     * when a formula is missing from pre-compiled JSON shards.
     */
    public function synthesizeFormulaExplanation(string $latex): array
    {
        if (empty($latex)) {
            return [];
        }

        $canonical = $this->canonicalizeLatex($latex);
        if (empty($canonical)) {
            return [];
        }

        $title = "Custom Physical Relation";
        $intro = "This mathematical identity represents a physical relationship between variables and differential operators.";
        $summary = "It defines how physical fields or particle states evolve and interact.";
        $interpretation = "The left-hand side of the relation establishes how spatial gradients or field variations are balanced by the right-hand side source or rate terms.";
        $symmetry = "Formulated in coordinate-free tensor or vector notation, maintaining spatial rotation and translation invariance.";
        $limits = "Subject to boundary constraints where field quantities decay or approach stationary states.";

        // 1. Classical Mechanics & Force / Acceleration / Newton's Second Law
        if (strpos($canonical, 'f=m') !== false || strpos($canonical, 'f=ma') !== false || (strpos($canonical, 'f=') !== false && (strpos($canonical, 'd^2') !== false || strpos($canonical, 'dt^2') !== false))) {
            $title = "Newton's Second Law of Motion (Differential Form)";
            $intro = "Relates the net vector force acting on a particle to its mass and the second time derivative of position (acceleration).";
            $summary = "The net vector force equals mass times instantaneous acceleration: \\mathbf{F} = m \\frac{d^2 \\mathbf{r}}{dt^2}.";
            $interpretation = "The differential operator \\frac{d^2 \\mathbf{r}}{dt^2} represents the instantaneous acceleration vector \\mathbf{a}. Multiplying by inertial mass \$m\$ determines the net force required to change the particle's state of motion.";
            $symmetry = "Galilean-invariant under constant velocity transformations; invariant under 3D spatial rotations and translations.";
            $limits = "Valid for constant-mass particles at non-relativistic speeds (\$v \\ll c\$) in inertial reference frames.";
        }
        // 2. Electromagnetism & Curl / Maxwell Limits
        elseif (strpos($canonical, 'curl') !== false || strpos($canonical, 'div') !== false) {
            if ((strpos($canonical, 'curle=0') !== false || strpos($canonical, 'curl=0') !== false) || (strpos($canonical, 'curle') !== false && strpos($canonical, 'curlb') !== false)) {
                $title = "Static Limits of Maxwell's Equations";
                $intro = "The steady-state or static limits of Maxwell's equations govern electromagnetic phenomena when charge distributions and currents are non-varying in time.";
                $summary = "Under static conditions where fields do not change over time, the electric field is irrotational (curl-free), while magnetic fields are generated purely by steady electric current density.";
                $interpretation = "In the static limit, the induced electric field from changing magnetic fields vanishes (\\nabla \\times \\mathbf{E} = 0), allowing the electric field to be represented as the gradient of a scalar electrostatic potential (\\mathbf{E} = -\\nabla V). Simultaneously, the displacement current term vanishes, causing the curl of the magnetic field to depend exclusively on static current density (\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J}).";
                $symmetry = "Originates from time-translation invariance (\\partial / \\partial t = 0) and local gauge symmetry under steady current distributions.";
                $limits = "Valid in non-radiating, low-frequency, or zero-frequency steady-state electrodynamics where inductive and displacement currents are negligible.";
            } elseif (strpos($canonical, 'curle') !== false) {
                $title = "Faraday's Law of Induction / Electric Field Curl";
                $intro = "Defines the curl of the electric field, relating rotational electric field circulation to changing magnetic fields.";
                $summary = "Changing magnetic flux generates an induced circulation in the surrounding electric field.";
                $interpretation = "The curl operator (\\nabla \\times \\mathbf{E}) measures the local vorticity or circulation of the electric field lines per unit area.";
                $symmetry = "Lorentz-covariant under relativistic transformations; invariant under spatial rotations.";
                $limits = "In the static limit (\\partial \\mathbf{B}/\\partial t = 0), the curl vanishes, reducing the field to electrostatic conservative form.";
            } elseif (strpos($canonical, 'curlb') !== false) {
                $title = "Ampère-Maxwell Law / Magnetic Field Curl";
                $intro = "Relates the spatial circulation of the magnetic field to electric current density and displacement currents.";
                $summary = "Magnetic field lines curl around moving electric charges and time-varying electric fields.";
                $interpretation = "The circulation of \\mathbf{B} around a closed loop is driven by the net current enclosed by that loop.";
                $symmetry = "Preserves gauge symmetry under electromagnetic gauge transformations.";
                $limits = "In vacuum with zero current density (\\mathbf{J}=0, \\partial \\mathbf{E}/\\partial t = 0), the curl vanishes.";
            }
        } elseif (strpos($canonical, 'delta') !== false || strpos($canonical, '\delta') !== false || strpos($latex, '\delta') !== false || strpos(strtolower($latex), 'bounded') !== false || strpos(strtolower($latex), 'field') !== false) {
            $isField = (strpos(strtolower($latex), 'field') !== false || strpos($canonical, 'phi') !== false || strpos($canonical, 'psi') !== false);
            $title = $isField ? 'Second Variation of Action in Field Theory ($\delta^2 S_{\text{field}}$)' : 'Second Variation of Action / Entropy Stability ($\delta^2 S_{\text{bounded}}$)';
            $intro = $isField
                ? 'The second variation of action in field theory, denoted as $\delta^2 S_{\text{field}}[\phi]$, represents the second-order functional derivative operator $\frac{\delta^2 S}{\delta \phi(x) \delta \phi(y)}$ acting on field perturbations $\delta \phi(x)$. It governs the local stability of classical vacuum states, soliton solutions, and cosmological background fields.'
                : 'Represents the second-order variation of action or thermodynamic entropy ($\delta^2 S$), used to establish local stability, convexity of thermodynamic potentials, and bounded oscillation modes in physical systems.';
            $summary = $isField
                ? 'The second variation of field action determines whether small field perturbations oscillate harmonically around a stable vacuum or grow exponentially due to tachyonic instability.'
                : 'A bounded second variation ($\delta^2 S \le 0$ or $|\delta^2 S| < \infty$) guarantees that small fluctuations around an equilibrium path or thermodynamic state remain stable and bounded over time.';
            $interpretation = $isField
                ? 'While setting the first variation to zero ($\delta S[\phi] = 0$) yields the classical field equations of motion (e.g., Klein-Gordon, Maxwell, or Einstein field equations), the second variation $\delta^2 S_{\text{field}}$ defines the fluctuation Hessian operator. A positive-definite second variation ($\delta^2 S_{\text{field}} > 0$) guarantees vacuum stability, whereas a negative eigenvalue ($\delta^2 S_{\text{field}} < 0$) signals a tachyonic mode leading to spontaneous symmetry breaking or vacuum decay. In quantum field theory, $\delta^2 S_{\text{field}}$ forms the inverse propagator kernel $\mathcal{D}^{-1}(x,y)$ for path-integral 1-loop quantum corrections.'
                : 'While the first variation ($\delta S = 0$) identifies stationary solutions (equations of motion or equilibrium states), the second variation ($\delta^2 S$) dictates system stability. A bounded or negative-definite second variation ensures that perturbation energies remain localized without exponential growth.';
            $symmetry = $isField
                ? 'Stemming from Hamilton\'s Principle of Stationary Action extended to continuous field degrees of freedom ($S[\phi] = \int \mathcal{L}(\phi, \partial_\mu \phi) \, d^4x$), the second variation operator preserves Poincaré spacetime invariance and gauge symmetries of the field Lagrangian.'
                : 'Derived from Hamilton\'s Principle of Least Action and the Second Law of Thermodynamics under variational field transformations.';
            $limits = $isField
                ? 'In the weak-field or linear perturbation regime ($\delta \phi \to 0$), higher-order functional derivatives $\mathcal{O}(\delta \phi^3)$ are negligible, reducing field dynamics to linear wave propagation. Under infinite spatial boundaries, field perturbations $\delta \phi(x)$ are required to satisfy square-integrable asymptotic fall-off conditions ($\delta \phi \to 0$ as $|x| \to \infty$).'
                : 'In the linear perturbation limit ($\delta S \to 0$), higher-order non-linear terms are negligible, reducing the variation to harmonic stability analysis.';
        }

        return [
            'id' => 'synthesized-' . substr(md5($latex), 0, 8),
            'title' => $title,
            'equation' => $latex,
            'conceptual_definition' => $intro,
            'intuitive_summary' => $summary,
            'interpretation' => $interpretation,
            'symmetry_origin' => $symmetry,
            'limits_and_boundary' => $limits,
            'unit_system' => 'SI',
            'status' => 'synthesized-ast'
        ];
    }
}
