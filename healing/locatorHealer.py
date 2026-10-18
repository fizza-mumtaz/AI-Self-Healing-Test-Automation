from difflib import SequenceMatcher
from playwright.sync_api import TimeoutError
from healing.geminiHealer import GeminiHealer

class LocatorHealer:

    def __init__(self, page):
        self.page = page
        self.geminiHealer = None

    def calculateSimilarity(self, original, candidate):
        original = original.strip("#").lower()
        candidate = candidate.lower()

        return SequenceMatcher(
            None,
            original,
            candidate
        ).ratio()

    def extractTokens(self, text):
        tokens = set()
        current = ""

        for char in (text or "").lower():
            if char.isalnum():
                current += char
            else:
                if len(current) >= 3:
                    tokens.add(current)
                current = ""

        if len(current) >= 3:
            tokens.add(current)

        return tokens

    def originalTargetTokens(self, originalLocator):
        genericTokens = {
            "add",
            "and",
            "aria",
            "btn",
            "button",
            "cart",
            "class",
            "click",
            "css",
            "data",
            "for",
            "href",
            "icon",
            "input",
            "label",
            "link",
            "name",
            "old",
            "remove",
            "role",
            "submit",
            "test",
            "text",
            "the",
            "type",
        }
        tokens = self.extractTokens(originalLocator)
        specificTokens = {token for token in tokens if token not in genericTokens}

        if specificTokens:
            return specificTokens

        return tokens

    def elementEvidenceTokens(self, element):
        values = []

        for attribute in [
            "id",
            "name",
            "data-test",
            "aria-label",
            "placeholder",
            "value",
            "title",
            "alt",
            "class",
            "href",
            "type",
        ]:
            value = element.get_attribute(attribute)

            if value:
                values.append(value)

        text = (element.text_content() or "").strip()

        if text:
            values.append(text)

        tokens = set()

        for value in values:
            tokens |= self.extractTokens(value)

        return tokens

    def suggestionMatchesOriginalTarget(self, originalLocator, element):
        requiredTokens = self.originalTargetTokens(originalLocator)

        if not requiredTokens:
            return False

        evidenceTokens = self.elementEvidenceTokens(element)

        return requiredTokens.issubset(evidenceTokens)

    def isValidForAction(self, element, action):

        tag = element.evaluate("el => el.tagName.toLowerCase()")
        role = element.get_attribute("role")
        inputType = (element.get_attribute("type") or "text").lower()

        if action == "fill":
            return (
                tag == "textarea"
                or (
                    tag == "input"
                    and inputType not in (
                        "button", "submit", "reset",
                        "checkbox", "radio", "file", "hidden"
                    )
                )
            )

        if action == "click":
            return (
                tag in ("button", "a", "select")
                or role == "button"
                or (
                    tag == "input"
                    and inputType in ("button", "submit", "reset")
                )
            )

        return False

    def findSimilarElement(self, originalLocator, action="click"):

        elements = self.page.locator(
            "button, input, textarea, select, a, [role='button']"
        ).all()

        bestLocator = None
        bestScore = 0
        secondBestScore = 0

        for element in elements:

            elementBestScore = 0
            elementBestLocator = None

            try:
                for attribute in ["id", "name", "data-test", "aria-label"]:

                    value = element.get_attribute(attribute)

                    if not value:
                        continue

                    score = self.calculateSimilarity(originalLocator, value)

                    if score > elementBestScore:
                        elementBestScore = score
                        elementBestLocator = f'[{attribute}="{value}"]'

            except TimeoutError:
                continue

            if elementBestScore > bestScore:
                secondBestScore = bestScore
                bestScore = elementBestScore
                bestLocator = elementBestLocator

            elif elementBestScore > secondBestScore:
                secondBestScore = elementBestScore

        if bestScore >= 0.7 and bestScore - secondBestScore >= 0.1 and bestLocator is not None:

            matchedElement = self.page.locator(bestLocator)

            if (
                matchedElement.count() == 1
                and matchedElement.is_visible()
                and matchedElement.is_enabled()
                and self.isValidForAction(matchedElement, action)
                and self.suggestionMatchesOriginalTarget(
                    originalLocator, matchedElement
                )
            ):
                return bestLocator

        return None

    def collectCandidateData(self):

        elements = self.page.locator(
            "button, input, textarea, select, a, [role='button']"
        ).all()

        lines = []
        fingerprints = set()

        for element in elements:

            try:
                tag = element.evaluate("el => el.tagName.toLowerCase()")
                text = (element.text_content() or "").strip()[:80]
                attrs = {}

                parts = [f"tag={tag}"]

                for attribute in ["id", "name", "data-test", "aria-label", "type", "placeholder"]:
                    value = element.get_attribute(attribute)

                    if not value:
                        continue

                    attrs[attribute] = value
                    parts.append(f"{attribute}={value}")

                if text:
                    parts.append(f'text="{text}"')

                fingerprints.add((
                    tag,
                    attrs.get("id"),
                    attrs.get("name"),
                    attrs.get("data-test"),
                    text,
                ))
                lines.append(" ".join(parts))

                if len(lines) >= 40:
                    break

            except TimeoutError:
                continue

        return "\n".join(lines), fingerprints

    def validateGeminiSuggestion(self, originalLocator, suggestion, fingerprints, action="click"):

        if not suggestion:
            raise Exception(f"Gemini healing failed for: {originalLocator}")

        suggestion = suggestion.strip().strip("`\"'").splitlines()[0].strip()

        if not suggestion or suggestion.upper() == "NONE":
            raise Exception(f"Gemini healing failed for: {originalLocator}")

        if suggestion.startswith("/") or suggestion.lower().startswith("xpath"):
            raise Exception(f"Unsafe Gemini replacement: {suggestion}")

        try:
            matchedElement = self.page.locator(suggestion)
            count = matchedElement.count()
        except Exception:
            raise Exception(f"Unsafe Gemini replacement: {suggestion}")

        if count != 1:
            raise Exception(f"Unsafe Gemini replacement: {suggestion}")

        if not matchedElement.is_visible() or not matchedElement.is_enabled():
            raise Exception(f"Unsafe Gemini replacement: {suggestion}")

        try:
            tag = matchedElement.evaluate("el => el.tagName.toLowerCase()")
            text = (matchedElement.text_content() or "").strip()[:80]
            fingerprint = (
                tag,
                matchedElement.get_attribute("id"),
                matchedElement.get_attribute("name"),
                matchedElement.get_attribute("data-test"),
                text,
            )
        except TimeoutError:
            raise Exception(f"Unsafe Gemini replacement: {suggestion}")

        allowedTags = ("button", "input", "textarea", "select", "a")

        role = matchedElement.get_attribute("role")

        if (
            (tag not in allowedTags and role != "button")
            or fingerprint not in fingerprints
        ):
            raise Exception(f"Unsafe Gemini replacement: {suggestion}")

        if not self.suggestionMatchesOriginalTarget(originalLocator, matchedElement):
            raise Exception(f"Unsafe Gemini replacement: {suggestion}")

        if not self.isValidForAction(matchedElement, action):
            raise Exception(f"Unsafe {action} replacement: {suggestion}")

        return suggestion

    def findWithGemini(self, originalLocator, action="click"):

        candidates, fingerprints = self.collectCandidateData()

        if not candidates or not fingerprints:
            raise Exception(f"No replacement found for: {originalLocator}")

        try:
            if self.geminiHealer is None:
                self.geminiHealer = GeminiHealer()

            suggestion = self.geminiHealer.suggestLocator(originalLocator, candidates)
            
        except Exception as error:
            raise RuntimeError(
                f"Gemini healing failed for {originalLocator}: {error}"
            ) from error

        return self.validateGeminiSuggestion(
            originalLocator, suggestion, fingerprints, action
        )

    def clickWithHealing(self, originalLocator):

        element = self.page.locator(originalLocator)

        try:
            element.wait_for(state="visible", timeout=3000)
            element.click()
            return
        except TimeoutError:
            pass

        healedLocator = self.findSimilarElement(originalLocator)
        source = "rule-based"

        if healedLocator is None:
            healedLocator = self.findWithGemini(originalLocator)
            source = "Gemini"

        healedElement = self.page.locator(healedLocator)

        if healedElement.count() != 1 or not healedElement.is_visible():
            raise Exception(f"Unsafe replacement: {healedLocator}")

        healedElement.click()

        print(
           f"[HEALING SUCCESS] "
           f"Method: {source} | "
           f"Original: {originalLocator} | "
           f"Replacement: {healedLocator}"
        )

    def fillWithHealing(self, originalLocator, value):

        element = self.page.locator(originalLocator)

        try:
            element.wait_for(state="visible", timeout=3000)
            element.fill(value)
            return
        except TimeoutError:
            pass

        healedLocator = self.findSimilarElement(originalLocator, action="fill")
        source = "rule-based"

        if healedLocator is None:
            healedLocator = self.findWithGemini(originalLocator, action="fill")
            source = "Gemini"

        healedElement = self.page.locator(healedLocator)

        if (
            healedElement.count() != 1
            or not healedElement.is_visible()
            or not healedElement.is_enabled()
        ):
            raise Exception(f"Unsafe replacement: {healedLocator}")

        tag = healedElement.evaluate("el => el.tagName.toLowerCase()")

        if tag not in ("input", "textarea"):
            raise Exception(f"Replacement is not an input field: {healedLocator}")

        healedElement.fill(value)

        print(
            f"[HEALING SUCCESS] "
            f"Action: fill | "
            f"Method: {source} | "
            f"Original: {originalLocator} | "
            f"Replacement: {healedLocator}"
        )
