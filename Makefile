.PHONY: sync-lakehouse-doc clean-lakehouse-doc

LAKEHOUSE_DOC_SRC ?= $(HOME)/IdeaProjects/lakehouse_doc_en
LAKEHOUSE_DOC_ROOT := lakehouse-doc-en
LAKEHOUSE_DOC_DST := $(LAKEHOUSE_DOC_ROOT)/references
LAKEHOUSE_DOC_TEMPLATE := $(LAKEHOUSE_DOC_ROOT)/SKILL.md.template
LAKEHOUSE_DOC_SKILL := $(LAKEHOUSE_DOC_ROOT)/SKILL.md
LAKEHOUSE_DOC_LLMS := $(LAKEHOUSE_DOC_SRC)/llms.txt

clean-lakehouse-doc:
	@echo "🧹 Cleaning $(LAKEHOUSE_DOC_DST) and $(LAKEHOUSE_DOC_SKILL)..."
	@rm -rf "$(LAKEHOUSE_DOC_DST)" "$(LAKEHOUSE_DOC_SKILL)"

sync-lakehouse-doc:
	@test -d "$(LAKEHOUSE_DOC_SRC)" || { echo "❌ Missing source directory: $(LAKEHOUSE_DOC_SRC)"; exit 1; }
	@test -f "$(LAKEHOUSE_DOC_TEMPLATE)" || { echo "❌ Missing template: $(LAKEHOUSE_DOC_TEMPLATE)"; exit 1; }
	@test -f "$(LAKEHOUSE_DOC_LLMS)" || { echo "❌ Missing llms.txt: $(LAKEHOUSE_DOC_LLMS)"; exit 1; }
	@echo "🧹 Cleaning $(LAKEHOUSE_DOC_DST)..."
	@rm -rf "$(LAKEHOUSE_DOC_DST)"
	@echo "📚 Syncing lakehouse-doc from $(LAKEHOUSE_DOC_SRC)..."
	@mkdir -p "$(LAKEHOUSE_DOC_DST)"
	rsync -a --prune-empty-dirs --include='*/' --exclude='RN[-_]*.md' --exclude='rn[-_]*.md' --exclude='CLAUDE.md' --exclude='AGENTS.md' --include='*.md' --include='llms-*.txt' --exclude='.*' --exclude='*' "$(LAKEHOUSE_DOC_SRC)/" "$(LAKEHOUSE_DOC_DST)/"
	@echo "✅ Synced $$(find "$(LAKEHOUSE_DOC_DST)" -type f | wc -l | tr -d ' ') files"
	@echo "📝 Generating $(LAKEHOUSE_DOC_SKILL) from template + llms.txt..."
	@set -e; \
		tmp=$$(mktemp "$(LAKEHOUSE_DOC_SKILL).tmp.XXXXXX"); \
		trap 'rm -f "$$tmp"' EXIT HUP INT TERM; \
		cat "$(LAKEHOUSE_DOC_TEMPLATE)" > "$$tmp"; \
		scripts/rewrite-llms-urls.sh "$(LAKEHOUSE_DOC_DST)" < "$(LAKEHOUSE_DOC_LLMS)" >> "$$tmp"; \
		chmod 644 "$$tmp"; \
		mv -f "$$tmp" "$(LAKEHOUSE_DOC_SKILL)"
	@echo "✅ Wrote $(LAKEHOUSE_DOC_SKILL) ($$(wc -l < "$(LAKEHOUSE_DOC_SKILL)" | tr -d ' ') lines)"
