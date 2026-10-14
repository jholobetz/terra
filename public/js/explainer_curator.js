/**
 * 🪐 Physics Lab: Equation Explainer - Curator Drawer & RBAC Module
 * Manages formula proposals, peer reviews, direct curation applying, and developer role switching.
 */

const ExplainerCurator = {
    initCuratorDrawer() {
        this.drawerOverlay = document.getElementById('curator-drawer-overlay');
        this.drawer = document.getElementById('curator-drawer');
        this.btnOpenDrawer = document.getElementById('btn-open-curator-drawer');
        this.btnCloseDrawer = document.getElementById('btn-close-curator-drawer');
        this.drawerRoleBadge = document.getElementById('drawer-user-role-badge');
        this.drawerFormulaIdLabel = document.getElementById('drawer-formula-id-label');
        this.drawerStagedCountBadge = document.getElementById('drawer-staged-count-badge');
        this.drawerStatusAlert = document.getElementById('drawer-status-alert');

        this.drawerFieldTitle = document.getElementById('drawer-field-title');
        this.drawerLatexInput = document.getElementById('drawer-latex-input');
        this.drawerHintInput = document.getElementById('drawer-hint-input');
        this.drawerFieldDefinition = document.getElementById('drawer-field-conceptual-definition');
        this.drawerFieldSummary = document.getElementById('drawer-field-intuitive-summary');
        this.drawerFieldInterpretation = document.getElementById('drawer-field-interpretation');
        this.drawerFieldSymmetry = document.getElementById('drawer-field-symmetry');
        this.drawerFieldLimits = document.getElementById('drawer-field-limits');
        this.drawerFieldDerivationSteps = document.getElementById('drawer-field-derivation-steps');

        this.drawerPreviewEquation = document.getElementById('drawer-preview-equation');
        this.drawerPreviewDefinition = document.getElementById('drawer-preview-definition');
        this.drawerPreviewLimits = document.getElementById('drawer-preview-limits');
        this.drawerReviewsContainer = document.getElementById('drawer-reviews-container');

        this.drawerBtnSuggest = document.getElementById('drawer-btn-suggest');
        this.drawerBtnApplyDirect = document.getElementById('drawer-btn-apply-direct');

        if (!this.drawer) return;

        // Open Drawer
        if (this.btnOpenDrawer) {
            this.btnOpenDrawer.addEventListener('click', () => {
                this.openCuratorDrawer();
            });
        }

        // Close Drawer
        if (this.btnCloseDrawer) {
            this.btnCloseDrawer.addEventListener('click', () => this.closeCuratorDrawer());
        }
        if (this.drawerOverlay) {
            this.drawerOverlay.addEventListener('click', () => this.closeCuratorDrawer());
        }

        // Tab Switching
        document.querySelectorAll('.drawer-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.drawer-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.drawer-tab-pane').forEach(p => p.style.display = 'none');

                tab.classList.add('active');
                const target = tab.getAttribute('data-tab');
                const pane = document.getElementById(`drawer-tab-content-${target}`);
                if (pane) pane.style.display = 'flex';

                if (target === 'preview') {
                    this.updateDrawerLivePreview();
                } else if (target === 'reviews') {
                    this.loadReviewsForDrawer();
                }
            });
        });

        // Live input updates for preview
        if (this.drawerLatexInput) {
            this.drawerLatexInput.addEventListener('input', () => this.updateDrawerLivePreview());
        }
        if (this.drawerHintInput) {
            this.drawerHintInput.addEventListener('input', () => this.updateDrawerLivePreview());
        }
        if (this.drawerFieldDefinition) {
            this.drawerFieldDefinition.addEventListener('input', () => this.updateDrawerLivePreview());
        }
        if (this.drawerFieldSummary) {
            this.drawerFieldSummary.addEventListener('input', () => this.updateDrawerLivePreview());
        }

        // Action: Submit Suggestion (Contributor Tier)
        if (this.drawerBtnSuggest) {
            this.drawerBtnSuggest.addEventListener('click', () => this.submitSuggestion());
        }

        // Action: Apply Directly (Curator/Admin Tier)
        if (this.drawerBtnApplyDirect) {
            this.drawerBtnApplyDirect.addEventListener('click', () => this.applyDirectRepair());
        }

        // Action: Fix LaTeX
        const btnFixLatex = document.getElementById('drawer-btn-fixlatex');
        if (btnFixLatex) {
            btnFixLatex.addEventListener('click', () => this.triggerFixLatex());
        }

        // Action: Auto-Draft
        const btnAutoDraft = document.getElementById('drawer-btn-autodraft');
        if (btnAutoDraft) {
            btnAutoDraft.addEventListener('click', () => this.triggerAutoDraft());
        }
    },

    openCuratorDrawer() {
        if (!this.drawer) return;

        const user = window.CURRENT_USER || { role: 'guest', display_name: 'Guest' };
        const formulaId = this.currentId || (this.currentFormula ? this.currentFormula.id : '');

        // Update Labels & Badges
        if (this.drawerRoleBadge) {
            this.drawerRoleBadge.textContent = user.role.toUpperCase();
            if (user.role === 'admin') {
                this.drawerRoleBadge.style.color = '#f43f5e';
                this.drawerRoleBadge.style.borderColor = 'rgba(244,63,94,0.4)';
            } else if (user.role === 'curator') {
                this.drawerRoleBadge.style.color = '#64ffda';
                this.drawerRoleBadge.style.borderColor = 'rgba(100,255,218,0.4)';
            } else {
                this.drawerRoleBadge.style.color = '#fbbf24';
                this.drawerRoleBadge.style.borderColor = 'rgba(251,191,36,0.4)';
            }
        }

        if (this.drawerFormulaIdLabel) {
            this.drawerFormulaIdLabel.textContent = formulaId ? `Formula ID: ${formulaId}` : 'Ad-hoc Equation (Unregistered)';
        }

        // Single-Developer Mode: Apply directly is always active
        if (this.drawerBtnApplyDirect) {
            this.drawerBtnApplyDirect.style.display = 'inline-block';
        }
        if (this.drawerBtnSuggest) {
            this.drawerBtnSuggest.style.display = 'none';
        }

        // Populate Fields
        const f = this.currentFormula || {};
        if (this.drawerFieldTitle) this.drawerFieldTitle.value = f.title || '';
        if (this.drawerLatexInput) this.drawerLatexInput.value = this.currentLatex || this.getCleanLatexFromEq(f.equation) || '';
        if (this.drawerHintInput) this.drawerHintInput.value = '';
        if (this.drawerFieldDefinition) this.drawerFieldDefinition.value = f.conceptual_definition || '';
        if (this.drawerFieldSummary) this.drawerFieldSummary.value = f.intuitive_summary || '';
        if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = f.interpretation || '';
        if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = f.symmetry_origin || '';
        if (this.drawerFieldLimits) this.drawerFieldLimits.value = f.limits_and_boundary || '';
        if (this.drawerFieldDerivationSteps) {
            this.drawerFieldDerivationSteps.value = (Array.isArray(f.derivation_steps) && f.derivation_steps.length > 0)
                ? JSON.stringify(f.derivation_steps, null, 2)
                : '';
        }

        // Clear alerts
        this.hideDrawerAlert();

        // Open Slide-Over
        this.drawerOverlay.style.display = 'block';
        setTimeout(() => {
            this.drawer.style.right = '0px';
            this.updateDrawerLivePreview();
        }, 10);

        this.loadReviewsForDrawer();
    },

    closeCuratorDrawer() {
        if (!this.drawer) return;
        this.drawer.style.right = '-560px';
        setTimeout(() => {
            this.drawerOverlay.style.display = 'none';
        }, 350);
    },

    updateDrawerLivePreview() {
        const latex = this.drawerLatexInput ? this.drawerLatexInput.value.trim() : '';
        const hint = this.drawerHintInput ? this.drawerHintInput.value.trim() : '';
        const limits = this.drawerFieldLimits ? this.drawerFieldLimits.value.trim() : '';
        const defVal = this.drawerFieldDefinition ? this.drawerFieldDefinition.value.trim() : '';
        const sumVal = this.drawerFieldSummary ? this.drawerFieldSummary.value.trim() : '';

        if (this.drawerPreviewEquation) {
            if (latex) {
                this.drawerPreviewEquation.textContent = `\\[ ${latex} \\]`;
            } else {
                this.drawerPreviewEquation.innerHTML = '<span style="opacity:0.5;">No equation entered</span>';
            }
        }

        if (this.drawerPreviewDefinition) {
            const defText = defVal || (this.currentFormula ? this.currentFormula.conceptual_definition : '') || '';
            const summaryText = sumVal || (this.currentFormula ? this.currentFormula.intuitive_summary : '') || '';
            let contentHtml = '';
            if (defText) {
                contentHtml += `<div style="font-weight: 500; color: #f8fafc; margin-bottom: 6px;">${this.wrapTextMathDelimiters(defText)}</div>`;
            }
            if (summaryText) {
                contentHtml += `<div style="color: var(--text-muted, #94a3b8); font-style: italic; border-left: 2px solid var(--accent-default, #64ffda); padding-left: 8px;">${this.wrapTextMathDelimiters(summaryText)}</div>`;
            }
            this.drawerPreviewDefinition.innerHTML = contentHtml || '<span style="opacity:0.5;">No definition specified</span>';
        }

        if (this.drawerPreviewLimits) {
            const previewText = hint || limits || (this.currentFormula ? this.currentFormula.limits_and_boundary : 'No limiting cases specified.');
            this.drawerPreviewLimits.innerHTML = this.wrapTextMathDelimiters(previewText);
        }

        const previewTargets = [this.drawerPreviewEquation, this.drawerPreviewLimits];
        if (this.drawerPreviewDefinition) previewTargets.push(this.drawerPreviewDefinition);
        this.triggerTypeset(previewTargets);
    },

    showDrawerAlert(message, isError = false) {
        if (!this.drawerStatusAlert) return;
        this.drawerStatusAlert.style.display = 'block';
        this.drawerStatusAlert.style.background = isError ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)';
        this.drawerStatusAlert.style.color = isError ? '#f43f5e' : '#10b981';
        this.drawerStatusAlert.style.border = isError ? '1px solid rgba(244, 63, 94, 0.3)' : '1px solid rgba(16, 185, 129, 0.3)';
        this.drawerStatusAlert.textContent = message;
    },

    hideDrawerAlert() {
        if (this.drawerStatusAlert) this.drawerStatusAlert.style.display = 'none';
    },

    submitSuggestion() {
        const formulaId = this.currentId || (this.currentFormula ? this.currentFormula.id : '') || 'synthesized-custom';
        const latex = (this.drawerLatexInput ? this.drawerLatexInput.value.trim() : '') || this.currentLatex;

        if (!latex) {
            this.showDrawerAlert('Please provide a LaTeX equation to submit a suggestion.', true);
            return;
        }

        let derivationSteps = null;
        if (this.drawerFieldDerivationSteps && this.drawerFieldDerivationSteps.value.trim()) {
            try {
                derivationSteps = JSON.parse(this.drawerFieldDerivationSteps.value.trim());
                if (!Array.isArray(derivationSteps)) throw new Error('Must be an array of step objects');
            } catch (e) {
                this.showDrawerAlert('Invalid JSON in Derivation Steps: ' + e.message, true);
                return;
            }
        }

        const payload = {
            formula_id: formulaId,
            latex: latex,
            hint: this.drawerHintInput ? this.drawerHintInput.value.trim() : '',
            prose: {
                title: this.drawerFieldTitle ? this.drawerFieldTitle.value.trim() : (this.currentFormula ? this.currentFormula.title : 'Custom Physical Relation'),
                conceptual_definition: this.drawerFieldDefinition ? this.drawerFieldDefinition.value.trim() : (this.currentFormula ? this.currentFormula.conceptual_definition : ''),
                intuitive_summary: this.drawerFieldSummary ? this.drawerFieldSummary.value.trim() : (this.currentFormula ? this.currentFormula.intuitive_summary : ''),
                interpretation: this.drawerFieldInterpretation ? this.drawerFieldInterpretation.value.trim() : '',
                symmetry_origin: this.drawerFieldSymmetry ? this.drawerFieldSymmetry.value.trim() : '',
                limits_and_boundary: this.drawerFieldLimits ? this.drawerFieldLimits.value.trim() : ''
            }
        };
        if (derivationSteps !== null) {
            payload.prose.derivation_steps = derivationSteps;
        }

        this.drawerBtnSuggest.disabled = true;
        this.drawerBtnSuggest.textContent = 'Submitting...';

        fetch('/physics/api/suggest-repair', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            this.drawerBtnSuggest.disabled = false;
            this.drawerBtnSuggest.textContent = 'Submit for Review';
            if (data.success) {
                this.showDrawerAlert('✓ Suggestion submitted to review queue successfully!');
                this.loadReviewsForDrawer();
            } else {
                this.showDrawerAlert(data.error || 'Failed to submit suggestion.', true);
            }
        })
        .catch(err => {
            this.drawerBtnSuggest.disabled = false;
            this.drawerBtnSuggest.textContent = 'Submit for Review';
            this.showDrawerAlert('Network error submitting suggestion.', true);
        });
    },

    applyDirectRepair() {
        const formulaId = this.currentId || (this.currentFormula ? this.currentFormula.id : '') || 'synthesized-custom';
        const latex = (this.drawerLatexInput ? this.drawerLatexInput.value.trim() : '') || this.currentLatex;

        if (!latex) {
            this.showDrawerAlert('Please provide a LaTeX equation to apply.', true);
            return;
        }

        let derivationSteps = null;
        if (this.drawerFieldDerivationSteps && this.drawerFieldDerivationSteps.value.trim()) {
            try {
                derivationSteps = JSON.parse(this.drawerFieldDerivationSteps.value.trim());
                if (!Array.isArray(derivationSteps)) throw new Error('Must be an array of step objects');
            } catch (e) {
                this.showDrawerAlert('Invalid JSON in Derivation Steps: ' + e.message, true);
                return;
            }
        }

        const payload = {
            formula_id: formulaId,
            latex: latex,
            hint: this.drawerHintInput ? this.drawerHintInput.value.trim() : '',
            prose: {
                title: this.drawerFieldTitle ? this.drawerFieldTitle.value.trim() : (this.currentFormula ? this.currentFormula.title : 'Custom Physical Relation'),
                conceptual_definition: this.drawerFieldDefinition ? this.drawerFieldDefinition.value.trim() : (this.currentFormula ? this.currentFormula.conceptual_definition : ''),
                intuitive_summary: this.drawerFieldSummary ? this.drawerFieldSummary.value.trim() : (this.currentFormula ? this.currentFormula.intuitive_summary : ''),
                interpretation: this.drawerFieldInterpretation ? this.drawerFieldInterpretation.value.trim() : '',
                symmetry_origin: this.drawerFieldSymmetry ? this.drawerFieldSymmetry.value.trim() : '',
                limits_and_boundary: this.drawerFieldLimits ? this.drawerFieldLimits.value.trim() : ''
            }
        };
        if (derivationSteps !== null) {
            payload.prose.derivation_steps = derivationSteps;
        }

        this.drawerBtnApplyDirect.disabled = true;
        this.drawerBtnApplyDirect.textContent = 'Applying...';

        fetch('/physics/api/apply-repair', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            this.drawerBtnApplyDirect.disabled = false;
            this.drawerBtnApplyDirect.textContent = '⚡ Apply & Sync Directly';
            if (data.success && data.data && data.data.formula) {
                this.showDrawerAlert('✓ Changes committed to shard and database synchronized!');
                this.currentId = data.data.formula.id;
                this.renderFormula(data.data.formula, this.currentSubtopics || []);
                this.currentLatex = data.data.clean_equation;
                this.compileMathJax(this.currentLatex);
                if (this.drawerFormulaIdLabel) {
                    this.drawerFormulaIdLabel.textContent = `Formula ID: ${data.data.formula.id}`;
                }
                if (window.history && window.history.replaceState) {
                    const newUrl = window.location.pathname + '?id=' + encodeURIComponent(data.data.formula.id);
                    window.history.replaceState(null, '', newUrl);
                }
            } else {
                this.showDrawerAlert(data.error || 'Failed to apply repair.', true);
            }
        })
        .catch(err => {
            this.drawerBtnApplyDirect.disabled = false;
            this.drawerBtnApplyDirect.textContent = '⚡ Apply & Sync Directly';
            this.showDrawerAlert('Network error applying repair.', true);
        });
    },

    loadReviewsForDrawer() {
        const formulaId = this.currentId || (this.currentFormula ? this.currentFormula.id : '');
        if (!this.drawerReviewsContainer) return;

        const url = formulaId ? `/physics/api/reviews?formula_id=${encodeURIComponent(formulaId)}` : '/physics/api/reviews';

        fetch(url)
            .then(res => res.json())
            .then(data => {
                if (data.success && Array.isArray(data.reviews)) {
                    if (this.drawerStagedCountBadge) {
                        this.drawerStagedCountBadge.textContent = data.reviews.length;
                    }
                    this.renderReviewsList(data.reviews);
                }
            })
            .catch(() => {
                this.drawerReviewsContainer.innerHTML = '<div style="color:#f43f5e; font-size:0.8rem;">Failed to load reviews.</div>';
            });
    },

    renderReviewsList(reviews) {
        if (!this.drawerReviewsContainer) return;
        if (reviews.length === 0) {
            this.drawerReviewsContainer.innerHTML = `
                <div style="text-align: center; padding: 30px 10px; color: var(--text-muted, #94a3b8); font-size: 0.82rem;">
                    No pending suggestions for this formula.
                </div>
            `;
            return;
        }

        const user = window.CURRENT_USER || { role: 'guest' };
        const canApprove = user.role === 'curator' || user.role === 'admin';

        let html = '';
        reviews.forEach(r => {
            html += `
                <div style="background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 14px; display: flex; flex-direction: column; gap: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.75rem; font-weight: 600; color: #f1f5f9;">${r.author_name} <small style="color:#94a3b8;">(${r.author_role})</small></span>
                        <span style="font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); text-transform: uppercase;">${r.status}</span>
                    </div>
                    ${r.proposed_latex ? `<div style="font-size: 0.75rem; color: #64ffda; font-family: 'Fira Code', monospace; background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 4px;">${r.proposed_latex}</div>` : ''}
                    ${r.hint_text ? `<div style="font-size: 0.78rem; color: #cbd5e1; line-height: 1.3;">${r.hint_text.slice(0, 150)}...</div>` : ''}
                    <div style="font-size: 0.68rem; color: #64748b;">${new Date(r.created_at).toLocaleString()}</div>
                    ${canApprove && r.status === 'pending' ? `
                        <div style="display: flex; gap: 8px; margin-top: 6px; justify-content: flex-end;">
                            <button onclick="EquationExplainer.rejectReview(${r.id})" style="padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; background: transparent; border: 1px solid rgba(244,63,94,0.4); color: #f43f5e; cursor: pointer;">Reject</button>
                            <button onclick="EquationExplainer.approveReview(${r.id})" style="padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; background: rgba(16,185,129,0.2); border: 1px solid rgba(16,185,129,0.4); color: #10b981; cursor: pointer;">✓ Approve &amp; Sync</button>
                        </div>
                    ` : ''}
                </div>
            `;
        });

        this.drawerReviewsContainer.innerHTML = html;
    },

    approveReview(reviewId) {
        fetch('/physics/api/reviews/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ review_id: reviewId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                this.showDrawerAlert('✓ Review approved and shard synced!');
                this.loadReviewsForDrawer();
                if (data.data && data.data.formula) {
                    this.renderFormula(data.data.formula, this.currentSubtopics || []);
                }
            } else {
                this.showDrawerAlert(data.error || 'Failed to approve review.', true);
            }
        });
    },

    rejectReview(reviewId) {
        const notes = prompt('Reason for rejection (optional):');
        fetch('/physics/api/reviews/reject', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ review_id: reviewId, notes: notes })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                this.showDrawerAlert('Suggestion rejected.');
                this.loadReviewsForDrawer();
            } else {
                this.showDrawerAlert(data.error || 'Failed to reject review.', true);
            }
        });
    },

    initDevRoleSwitcher() {
        const select = document.getElementById('dev-role-select');
        if (!select) return;

        const user = window.CURRENT_USER || { role: 'admin' };
        select.value = user.role || 'admin';

        select.addEventListener('change', () => {
            const newRole = select.value;
            fetch('/physics/api/auth/switch-role', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: newRole })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.user) {
                    window.CURRENT_USER = data.user;
                    if (this.drawerRoleBadge) {
                        this.drawerRoleBadge.textContent = data.user.role.toUpperCase();
                    }
                    const isPrivileged = data.user.role === 'curator' || data.user.role === 'admin';
                    if (this.drawerBtnApplyDirect) {
                        this.drawerBtnApplyDirect.style.display = isPrivileged ? 'inline-block' : 'none';
                    }
                    this.loadReviewsForDrawer();
                }
            });
        });
    },

    triggerAutoDraft() {
        const latex = (this.drawerLatexInput ? this.drawerLatexInput.value.trim() : '') || this.currentLatex;
        if (!latex) {
            this.showDrawerAlert('Please provide a LaTeX equation to auto-draft.', true);
            return;
        }

        const btnAutoDraft = document.getElementById('drawer-btn-autodraft');
        const originalHtml = btnAutoDraft ? btnAutoDraft.innerHTML : '';
        if (btnAutoDraft) {
            btnAutoDraft.disabled = true;
            btnAutoDraft.style.opacity = '0.7';
            btnAutoDraft.innerHTML = `<span style="display:inline-block; width:9px; height:9px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:explainer-spin 0.8s linear infinite; margin-right:4px;"></span> Drafting...`;
        }

        if (!document.getElementById('explainer-spin-style')) {
            const style = document.createElement('style');
            style.id = 'explainer-spin-style';
            style.textContent = `@keyframes explainer-spin { 100% { transform: rotate(360deg); } }`;
            document.head.appendChild(style);
        }

        const adminKey = localStorage.getItem('terra_admin_key') || '';

        fetch(`${BASE_URL}/physics/api/define-formula`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Terra-Admin-Key': adminKey
            },
            body: JSON.stringify({ latex: latex })
        })
        .then(res => res.json())
        .then(data => {
            if (btnAutoDraft) {
                btnAutoDraft.disabled = false;
                btnAutoDraft.style.opacity = '1';
                btnAutoDraft.innerHTML = originalHtml;
            }

            if (data.success && data.formula) {
                const f = data.formula;
                if (this.drawerFieldTitle) this.drawerFieldTitle.value = f.title || '';
                if (this.drawerFieldDefinition) this.drawerFieldDefinition.value = f.conceptual_definition || '';
                if (this.drawerFieldSummary) this.drawerFieldSummary.value = f.intuitive_summary || '';
                if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = f.interpretation || '';
                if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = f.symmetry_origin || '';
                if (this.drawerFieldLimits) this.drawerFieldLimits.value = f.limits_and_boundary || '';

                if (this.conceptualIntroCard) {
                    const definition = this.wrapTextMathDelimiters(f.conceptual_definition || f.title);
                    const summary = this.wrapTextMathDelimiters(f.intuitive_summary || f.interpretation || '');
                    const sourceBadge = f.is_fallback
                        ? `<span style="font-size: 0.68rem; padding: 2px 8px; border-radius: 4px; background: rgba(234, 179, 8, 0.12); color: #fbbf24; border: 1px solid rgba(234, 179, 8, 0.28); font-weight: 600; text-transform: none; letter-spacing: normal;">⚠️ Local Heuristic ($0.00)</span>`
                        : (f.source && f.source.includes('antigravity')
                            ? `<span style="font-size: 0.68rem; padding: 2px 8px; border-radius: 4px; background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.35); font-weight: 600; text-transform: none; letter-spacing: normal;">🪐 Antigravity Agent ($0.00)</span>`
                            : `<span style="font-size: 0.68rem; padding: 2px 8px; border-radius: 4px; background: rgba(16, 185, 129, 0.12); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.28); font-weight: 600; text-transform: none; letter-spacing: normal;">⚡ Gemini Free Tier ($0.00)</span>`);

                    this.conceptualIntroCard.style.display = 'flex';
                    this.conceptualIntroCard.innerHTML = `
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                            <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                                ✦ Explanation (Auto-Draft)
                            </h4>
                            ${sourceBadge}
                        </div>
                        <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                            ${definition}
                        </div>
                        ${summary ? `<div class="intuitive-summary" style="font-size: 0.92rem; line-height: 1.5; color: var(--text-muted, #94a3b8); border-left: 2px solid var(--accent-default, #64ffda); padding-left: 12px; font-style: italic; margin-top: 4px;">
                            ${summary}
                        </div>` : ''}
                    `;
                    this.triggerTypeset([this.conceptualIntroCard]);
                }
                if (this.currentFormula) {
                    this.currentFormula.title = f.title || this.currentFormula.title;
                    this.currentFormula.conceptual_definition = f.conceptual_definition || '';
                    this.currentFormula.intuitive_summary = f.intuitive_summary || '';
                    this.currentFormula.interpretation = f.interpretation || '';
                    this.currentFormula.symmetry_origin = f.symmetry_origin || '';
                    this.currentFormula.limits_and_boundary = f.limits_and_boundary || '';
                }

                if (f.is_fallback) {
                    this.showDrawerAlert('⚠️ Offline heuristic scaffold populated (AI Studio busy). Review and enrich in Live Preview before saving.', true);
                } else {
                    this.showDrawerAlert('✓ Gemini Free Tier draft populated! Review in Live Preview before saving.');
                }
                this.updateDrawerLivePreview();
            } else {
                const synthesis = this.synthesizeCustomOverview(latex);
                if (this.drawerFieldTitle) this.drawerFieldTitle.value = this.currentFormula ? this.currentFormula.title : (synthesis.title || 'Custom Physical Relation');
                if (this.drawerFieldDefinition) this.drawerFieldDefinition.value = synthesis.intro || '';
                if (this.drawerFieldSummary) this.drawerFieldSummary.value = synthesis.summary || '';
                if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = synthesis.intro || '';
                if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = 'Invariance derived from constitutive dynamical equations.';
                if (this.drawerFieldLimits) this.drawerFieldLimits.value = synthesis.summary || '';

                if (this.conceptualIntroCard) {
                    const definition = this.wrapTextMathDelimiters(synthesis.intro);
                    const summary = this.wrapTextMathDelimiters(synthesis.summary);
                    this.conceptualIntroCard.style.display = 'flex';
                    this.conceptualIntroCard.innerHTML = `
                        <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                            ✦ Explanation (Auto-Draft)
                        </h4>
                        <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                            ${definition}
                        </div>
                        <div class="intuitive-summary" style="font-size: 0.92rem; line-height: 1.5; color: var(--text-muted, #94a3b8); border-left: 2px solid var(--accent-default, #64ffda); padding-left: 12px; font-style: italic; margin-top: 4px;">
                            ${summary}
                        </div>
                    `;
                    this.triggerTypeset([this.conceptualIntroCard]);
                }
                if (this.currentFormula) {
                    this.currentFormula.conceptual_definition = synthesis.intro;
                    this.currentFormula.intuitive_summary = synthesis.summary;
                }

                this.showDrawerAlert('✓ Auto-draft synthesized from equation AST. Review before submitting.');
                this.updateDrawerLivePreview();
            }
        })
        .catch(err => {
            if (btnAutoDraft) {
                btnAutoDraft.disabled = false;
                btnAutoDraft.style.opacity = '1';
                btnAutoDraft.innerHTML = originalHtml;
            }
            const synthesis = this.synthesizeCustomOverview(latex);
            if (this.drawerFieldTitle) this.drawerFieldTitle.value = this.currentFormula ? this.currentFormula.title : (synthesis.title || 'Custom Physical Relation');
            if (this.drawerFieldDefinition) this.drawerFieldDefinition.value = synthesis.intro || '';
            if (this.drawerFieldSummary) this.drawerFieldSummary.value = synthesis.summary || '';
            if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = synthesis.intro || '';
            if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = 'Invariance derived from constitutive dynamical equations.';
            if (this.drawerFieldLimits) this.drawerFieldLimits.value = synthesis.summary || '';

            if (this.conceptualIntroCard) {
                const definition = this.wrapTextMathDelimiters(synthesis.intro);
                const summary = this.wrapTextMathDelimiters(synthesis.summary);
                this.conceptualIntroCard.style.display = 'flex';
                this.conceptualIntroCard.innerHTML = `
                    <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                        ✦ Explanation (Auto-Draft)
                    </h4>
                    <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                        ${definition}
                    </div>
                    <div class="intuitive-summary" style="font-size: 0.92rem; line-height: 1.5; color: var(--text-muted, #94a3b8); border-left: 2px solid var(--accent-default, #64ffda); padding-left: 12px; font-style: italic; margin-top: 4px;">
                        ${summary}
                    </div>
                `;
                this.triggerTypeset([this.conceptualIntroCard]);
            }
            if (this.currentFormula) {
                this.currentFormula.conceptual_definition = synthesis.intro;
                this.currentFormula.intuitive_summary = synthesis.summary;
            }

            this.showDrawerAlert('✓ Auto-draft synthesized from equation AST.');
            this.updateDrawerLivePreview();
        });
    },

    showActionProgress(percent, msg, isDone = false, isError = false) {
        const container = document.getElementById('drawer-action-progress-container');
        const fill = document.getElementById('drawer-progress-bar-fill');
        const statusMsg = document.getElementById('drawer-progress-status-msg');
        const percentLabel = document.getElementById('drawer-progress-percent');
        const statusText = document.getElementById('drawer-progress-status-text');

        if (!container || !fill || !statusMsg || !percentLabel) return;

        container.style.display = 'flex';
        fill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
        percentLabel.textContent = `${Math.round(percent)}%`;
        statusMsg.textContent = msg;

        if (isError) {
            fill.style.background = '#f43f5e';
            if (statusText) statusText.style.color = '#f43f5e';
        } else if (isDone) {
            fill.style.background = '#64ffda';
            if (statusText) statusText.style.color = '#64ffda';
        } else {
            fill.style.background = 'linear-gradient(90deg, #38bdf8, #64ffda)';
            if (statusText) statusText.style.color = '#38bdf8';
        }
    },

    hideActionProgress(delay = 1000) {
        setTimeout(() => {
            const container = document.getElementById('drawer-action-progress-container');
            if (container) {
                container.style.display = 'none';
            }
        }, delay);
    },

    triggerFixLatex() {
        const latex = (this.drawerLatexInput ? this.drawerLatexInput.value.trim() : '') || this.currentLatex;
        if (!latex) {
            this.showDrawerAlert('Please provide a LaTeX equation to fix.', true);
            return;
        }

        const btnFixLatex = document.getElementById('drawer-btn-fixlatex');
        const originalHtml = btnFixLatex ? btnFixLatex.innerHTML : '';
        if (btnFixLatex) {
            btnFixLatex.disabled = true;
            btnFixLatex.style.opacity = '0.7';
            btnFixLatex.innerHTML = `<span style="display:inline-block; width:9px; height:9px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:explainer-spin 0.8s linear infinite; margin-right:4px;"></span> Fixing...`;
        }

        this.showActionProgress(15, 'Validating syntax & searching formula index...');

        const formulaId = this.currentId || (this.currentFormula ? this.currentFormula.id : '') || 'synthesized-custom';
        const hint = this.drawerHintInput ? this.drawerHintInput.value.trim() : '';

        const payload = {
            url: window.location.href,
            formula_id: formulaId,
            latex: latex,
            hint: hint
        };

        const t1 = setTimeout(() => this.showActionProgress(45, 'Sanitizing TeX tokens & structuring narrative...'), 180);
        const t2 = setTimeout(() => this.showActionProgress(75, 'Updating JSON shard & synchronizing MariaDB...'), 420);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 20000);

        const baseUrl = (typeof BASE_URL !== 'undefined') ? BASE_URL : '';
        fetch(`${baseUrl}/physics/api/apply-repair`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload),
            signal: controller.signal
        })
        .then(async res => {
            clearTimeout(timeoutId);
            clearTimeout(t1);
            clearTimeout(t2);
            let data;
            try {
                data = await res.json();
            } catch (e) {
                throw new Error(`HTTP ${res.status}: Server returned invalid response.`);
            }
            if (!res.ok && data && data.error) {
                throw new Error(data.error);
            }
            return data;
        })
        .then(data => {
            if (btnFixLatex) {
                btnFixLatex.disabled = false;
                btnFixLatex.style.opacity = '1';
                btnFixLatex.innerHTML = originalHtml;
            }

            if (data.success && data.data && data.data.formula) {
                this.showActionProgress(100, '✓ Repair complete! MathJax synced.', true, false);
                this.hideActionProgress(1400);

                const f = data.data.formula;
                this.currentFormula = f;
                this.currentId = f.id;
                this.currentLatex = data.data.clean_equation || f.equation;

                if (this.latexInput) this.latexInput.value = this.currentLatex;
                if (this.drawerLatexInput) this.drawerLatexInput.value = this.currentLatex;
                if (this.drawerFieldTitle) this.drawerFieldTitle.value = f.title || '';
                if (this.drawerFieldDefinition) this.drawerFieldDefinition.value = f.conceptual_definition || '';
                if (this.drawerFieldSummary) this.drawerFieldSummary.value = f.intuitive_summary || '';
                if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = f.interpretation || '';
                if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = f.symmetry_origin || '';
                if (this.drawerFieldLimits) this.drawerFieldLimits.value = f.limits_and_boundary || '';

                if (this.drawerFormulaIdLabel) {
                    this.drawerFormulaIdLabel.textContent = `Formula ID: ${f.id}`;
                }

                this.renderFormula(f, this.currentSubtopics || []);
                this.compileMathJax(this.currentLatex);
                this.updateDrawerLivePreview();

                const targets = [];
                if (this.mathRenderTarget) targets.push(this.mathRenderTarget);
                if (this.conceptualIntroCard) targets.push(this.conceptualIntroCard);
                if (this.aiScenariosList) targets.push(this.aiScenariosList);
                if (this.drawerPreviewTarget) targets.push(this.drawerPreviewTarget);
                if (targets.length > 0) {
                    this.triggerTypeset(targets);
                }

                this.showDrawerAlert('✓ LaTeX decorrupted, hint applied, and shard/database synchronized!');

                if (window.history && window.history.replaceState) {
                    const newUrl = window.location.pathname + '?id=' + encodeURIComponent(f.id);
                    window.history.replaceState(null, '', newUrl);
                }
            } else {
                this.showActionProgress(100, `Error: ${data.error || 'Failed to fix LaTeX.'}`, false, true);
                this.hideActionProgress(3000);
                this.showDrawerAlert(data.error || 'Failed to fix LaTeX.', true);
            }
        })
        .catch(err => {
            clearTimeout(timeoutId);
            clearTimeout(t1);
            clearTimeout(t2);

            if (btnFixLatex) {
                btnFixLatex.disabled = false;
                btnFixLatex.style.opacity = '1';
                btnFixLatex.innerHTML = originalHtml;
            }

            const isTimeout = err.name === 'AbortError';
            const errorMsg = isTimeout ? 'Request timed out after 20 seconds.' : (err.message || 'Error while running Fix LaTeX.');

            this.showActionProgress(100, errorMsg, false, true);
            this.hideActionProgress(3000);

            console.error('Fix LaTeX error:', err);
            this.showDrawerAlert(errorMsg, true);
        });
    }
};

if (typeof window !== 'undefined') {
    window.ExplainerCurator = ExplainerCurator;
    if (window.EquationExplainer) {
        Object.assign(window.EquationExplainer, ExplainerCurator);
    }
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExplainerCurator;
}
