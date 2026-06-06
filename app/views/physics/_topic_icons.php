<?php
if (!function_exists('get_topic_icon_and_class')) {
    // Map slugs to classes and custom SVG icons
    function get_topic_icon_and_class(string $slug): array {
        switch ($slug) {
            case 'classical-mechanics':
                return [
                    'class' => 'card-classical',
                    'theme' => 'classical',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="1.2" fill="none" stroke-dasharray="3 3" opacity="0.3"/>
                            <ellipse cx="50" cy="50" rx="40" ry="12" stroke="currentColor" stroke-width="1.2" fill="none" transform="rotate(-30 50 50)"/>
                            <ellipse cx="50" cy="50" rx="40" ry="12" stroke="currentColor" stroke-width="1.2" fill="none" transform="rotate(60 50 50)" opacity="0.4"/>
                            <line x1="50" y1="10" x2="50" y2="90" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            <circle cx="50" cy="50" r="4" fill="currentColor"/>
                            <line x1="50" y1="50" x2="78" y2="34" stroke="var(--accent-classical)" stroke-width="2"/>
                        </svg>'
                ];
            case 'electromagnetism':
                return [
                    'class' => 'card-electromagnetism',
                    'theme' => 'electromagnetism',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <path d="M 50 20 C 10 20, 10 80, 50 80" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                            <path d="M 50 20 C 90 20, 90 80, 50 80" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                            <path d="M 50 10 C -10 10, -10 90, 50 90" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.2"/>
                            <path d="M 50 10 C 110 10, 110 90, 50 90" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.2"/>
                            <rect x="45" y="30" width="10" height="40" rx="3" fill="currentColor" opacity="0.1"/>
                            <line x1="50" y1="23" x2="50" y2="77" stroke="currentColor" stroke-width="2"/>
                            <path d="M 33 50 Q 41.5 40, 50 50 T 67 50" fill="none" stroke="var(--accent-electromagnetism)" stroke-width="2" stroke-linecap="round"/>
                            <circle cx="50" cy="23" r="3" fill="#ef4444"/>
                            <circle cx="50" cy="77" r="3" fill="#3b82f6"/>
                        </svg>'
                ];
            case 'relativity':
                return [
                    'class' => 'card-relativity',
                    'theme' => 'relativity',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <path d="M 10 50 Q 50 75, 90 50" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                            <path d="M 10 60 Q 50 85, 90 60" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                            <path d="M 10 40 Q 50 65, 90 40" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                            <path d="M 50 10 Q 75 50, 50 90" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                            <path d="M 40 10 Q 65 50, 40 90" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                            <path d="M 60 10 Q 85 50, 60 90" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                            <polygon points="50,50 30,22 70,22" fill="rgba(139, 92, 246, 0.1)" stroke="currentColor" stroke-width="1.2"/>
                            <polygon points="50,50 30,78 70,78" fill="rgba(139, 92, 246, 0.05)" stroke="currentColor" stroke-width="1.2" opacity="0.5"/>
                            <circle cx="50" cy="50" r="3" fill="var(--accent-relativity)"/>
                        </svg>'
                ];
            case 'quantum-physics':
                return [
                    'class' => 'card-quantum',
                    'theme' => 'quantum',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <path d="M 10 50 C 25 50, 30 20, 35 50 C 40 80, 45 10, 50 50 C 55 90, 60 20, 65 50 C 70 80, 75 50, 90 50" fill="none" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M 10 50 Q 50 5, 90 50" fill="none" stroke="var(--accent-quantum)" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.5"/>
                            <path d="M 10 50 Q 50 95, 90 50" fill="none" stroke="var(--accent-quantum)" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.5"/>
                            <circle cx="50" cy="50" r="3" fill="currentColor"/>
                            <circle cx="43" cy="35" r="2" fill="currentColor" opacity="0.6"/>
                            <circle cx="57" cy="65" r="2" fill="currentColor" opacity="0.6"/>
                        </svg>'
                ];
            case 'astrophysics':
                return [
                    'class' => 'card-astrophysics',
                    'theme' => 'astrophysics',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <circle cx="50" cy="50" r="28" stroke="currentColor" stroke-width="1.2" fill="none" opacity="0.2"/>
                            <circle cx="50" cy="50" r="44" stroke="currentColor" stroke-width="1" stroke-dasharray="4 4" fill="none" opacity="0.3"/>
                            <path d="M 50 15 C 65 30, 65 70, 50 85" fill="none" stroke="currentColor" stroke-width="1" opacity="0.25"/>
                            <path d="M 50 15 C 35 30, 35 70, 50 85" fill="none" stroke="currentColor" stroke-width="1" opacity="0.25"/>
                            <path d="M 50 50 Q 58 35, 75 40 T 65 65 T 35 60 T 45 42" fill="none" stroke="var(--accent-astrophysics)" stroke-width="2" stroke-linecap="round"/>
                            <circle cx="50" cy="50" r="7" fill="#030712" stroke="var(--accent-astrophysics)" stroke-width="1.5"/>
                            <circle cx="75" cy="40" r="2" fill="currentColor"/>
                            <circle cx="35" cy="60" r="1.5" fill="currentColor"/>
                        </svg>'
                ];
            case 'thermodynamics-statistical-mechanics':
                return [
                    'class' => 'card-thermodynamics',
                    'theme' => 'thermodynamics',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <rect x="20" y="20" width="60" height="60" rx="6" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.3"/>
                            <circle cx="35" cy="35" r="3" fill="currentColor"/>
                            <line x1="35" y1="35" x2="48" y2="42" stroke="currentColor" stroke-width="1" opacity="0.5"/>
                            <circle cx="65" cy="45" r="3" fill="currentColor"/>
                            <line x1="65" y1="45" x2="52" y2="52" stroke="currentColor" stroke-width="1" opacity="0.5"/>
                            <circle cx="45" cy="65" r="3" fill="currentColor"/>
                            <line x1="45" y1="65" x2="35" y2="52" stroke="currentColor" stroke-width="1" opacity="0.5"/>
                            <path d="M 25 80 Q 37.5 70, 50 80 T 75 80" fill="none" stroke="var(--accent-thermodynamics)" stroke-width="2" stroke-linecap="round"/>
                            <path d="M 25 74 Q 37.5 64, 50 74 T 75 74" fill="none" stroke="var(--accent-thermodynamics)" stroke-width="1" opacity="0.4"/>
                        </svg>'
                ];
            case 'fluids-nonlinear':
                return [
                    'class' => 'card-fluids',
                    'theme' => 'fluids',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <path d="M 15 25 Q 35 15, 55 35 T 85 25" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                            <path d="M 15 75 Q 35 65, 55 85 T 85 75" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                            <path d="M 50 50 C 70 30, 80 50, 50 60 C 20 70, 30 50, 50 50 Z" fill="none" stroke="var(--accent-fluids)" stroke-width="1.8" stroke-linejoin="round"/>
                            <path d="M 47 47 C 72 25, 85 47, 47 63 C 12 75, 22 47, 47 47 Z" fill="none" stroke="var(--accent-fluids)" stroke-width="1" opacity="0.4"/>
                            <circle cx="50" cy="50" r="2" fill="var(--accent-fluids)"/>
                        </svg>'
                ];
            case 'condensed-matter':
                return [
                    'class' => 'card-condensed',
                    'theme' => 'condensed',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <line x1="30" y1="30" x2="70" y2="30" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <line x1="30" y1="70" x2="70" y2="70" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <line x1="30" y1="30" x2="30" y2="70" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <line x1="70" y1="30" x2="70" y2="70" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <line x1="30" y1="30" x2="45" y2="45" stroke="currentColor" stroke-width="0.8" opacity="0.2"/>
                            <line x1="70" y1="30" x2="85" y2="45" stroke="currentColor" stroke-width="0.8" opacity="0.2"/>
                            <line x1="30" y1="70" x2="45" y2="85" stroke="currentColor" stroke-width="0.8" opacity="0.2"/>
                            <line x1="70" y1="70" x2="85" y2="85" stroke="currentColor" stroke-width="0.8" opacity="0.2"/>
                            <path d="M 30 30 L 70 30 L 70 70 L 30 70 Z" fill="rgba(132, 204, 22, 0.04)" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
                            <path d="M 30 30 L 50 50 L 70 70" fill="none" stroke="var(--accent-condensed)" stroke-width="1.8"/>
                            <circle cx="30" cy="30" r="4.5" fill="currentColor"/>
                            <circle cx="70" cy="30" r="4.5" fill="currentColor"/>
                            <circle cx="70" cy="70" r="4.5" fill="currentColor"/>
                            <circle cx="30" cy="70" r="4.5" fill="currentColor"/>
                            <circle cx="50" cy="50" r="5" fill="var(--accent-condensed)"/>
                        </svg>'
                ];
            case 'standard-model':
                return [
                    'class' => 'card-standard-model',
                    'theme' => 'standard-model',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <circle cx="50" cy="50" r="36" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3" fill="none" opacity="0.3"/>
                            <path d="M 32 38 Q 50 62, 68 38" fill="none" stroke="var(--accent-standard-model)" stroke-width="1.5"/>
                            <path d="M 32 38 Q 50 20, 68 38" fill="none" stroke="var(--accent-standard-model)" stroke-width="1.5" opacity="0.4"/>
                            <circle cx="32" cy="38" r="4" fill="currentColor"/>
                            <circle cx="68" cy="38" r="4" fill="currentColor"/>
                            <circle cx="50" cy="68" r="4" fill="currentColor"/>
                            <line x1="32" y1="38" x2="50" y2="68" stroke="currentColor" stroke-width="0.8" opacity="0.4"/>
                            <line x1="68" y1="38" x2="50" y2="68" stroke="currentColor" stroke-width="0.8" opacity="0.4"/>
                            <line x1="32" y1="38" x2="68" y2="38" stroke="currentColor" stroke-width="0.8" opacity="0.4"/>
                            <circle cx="50" cy="50" r="6" fill="none" stroke="var(--accent-standard-model)" stroke-width="1.5"/>
                        </svg>'
                ];
            case 'theoretical-physics':
                return [
                    'class' => 'card-theoretical',
                    'theme' => 'theoretical',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <line x1="15" y1="20" x2="35" y2="50" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                            <line x1="15" y1="80" x2="35" y2="50" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                            <path d="M 35 50 Q 50 42, 65 50" fill="none" stroke="var(--accent-theoretical)" stroke-width="2" stroke-linecap="round"/>
                            <path d="M 35 50 Q 50 58, 65 50" fill="none" stroke="var(--accent-theoretical)" stroke-width="2" stroke-linecap="round" opacity="0.3"/>
                            <line x1="65" y1="50" x2="85" y2="20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                            <line x1="65" y1="50" x2="85" y2="80" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                            <circle cx="35" cy="50" r="3.5" fill="currentColor"/>
                            <circle cx="65" cy="50" r="3.5" fill="currentColor"/>
                        </svg>'
                ];
            case 'mathematical-methods':
                return [
                    'class' => 'card-math-methods',
                    'theme' => 'math-methods',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <line x1="50" y1="10" x2="50" y2="90" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <line x1="10" y1="50" x2="90" y2="50" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <path d="M 50 50 C 35 30, 20 50, 50 75 C 80 50, 65 30, 50 50 Z" fill="none" stroke="var(--accent-math-methods)" stroke-width="1.8" stroke-linecap="round"/>
                            <circle cx="38" cy="45" r="2.5" fill="currentColor"/>
                            <circle cx="62" cy="55" r="2.5" fill="currentColor"/>
                            <path d="M 52 35 L 56 31 L 51 29" fill="none" stroke="var(--accent-math-methods)" stroke-width="1.2"/>
                        </svg>'
                ];
            case 'philosophy-of-physics':
                return [
                    'class' => 'card-philosophy',
                    'theme' => 'philosophy',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <path d="M 20 50 Q 50 25, 80 50" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                            <path d="M 20 50 Q 50 75, 80 50" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                            <path d="M 50 50 L 50 15" stroke="var(--accent-philosophy)" stroke-width="1" opacity="0.4"/>
                            <path d="M 50 50 L 78 30" stroke="var(--accent-philosophy)" stroke-width="1" opacity="0.4"/>
                            <path d="M 50 50 L 50 85" stroke="var(--accent-philosophy)" stroke-width="1.8"/>
                            <circle cx="50" cy="50" r="9" fill="none" stroke="currentColor" stroke-width="1.2"/>
                            <circle cx="50" cy="50" r="4" fill="var(--accent-philosophy)"/>
                        </svg>'
                ];
            default:
                return [
                    'class' => 'card-default',
                    'theme' => 'default',
                    'svg' => '
                        <svg viewBox="0 0 100 100" class="card-icon">
                            <polygon points="50,15 80,35 80,65 50,85 20,65 20,35" fill="none" stroke="currentColor" stroke-width="1.2"/>
                            <line x1="50" y1="15" x2="50" y2="85" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <line x1="20" y1="35" x2="80" y2="65" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <line x1="20" y1="65" x2="80" y2="35" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                            <circle cx="50" cy="50" r="7" fill="rgba(0, 210, 255, 0.08)" stroke="currentColor" stroke-width="1.2"/>
                        </svg>'
                ];
        }
    }
}
