import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { Markdown } from "@/components/Markdown";

describe("Markdown component", () => {
  it("renders null when source is empty or undefined", () => {
    const { container } = render(<Markdown source={undefined} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders basic Markdown text formatting", () => {
    const { container } = render(<Markdown source="**Bold text** and *italic text*" />);
    const strong = container.querySelector("strong");
    const em = container.querySelector("em");

    expect(strong).not.toBeNull();
    expect(strong?.textContent).toBe("Bold text");
    expect(em).not.toBeNull();
    expect(em?.textContent).toBe("italic text");
  });

  it("renders headers and list items", () => {
    const markdownText = `# Header 1\n- Item 1\n- Item 2`;
    const { container } = render(<Markdown source={markdownText} />);

    const h1 = container.querySelector("h1");
    const listItems = container.querySelectorAll("li");

    expect(h1?.textContent).toBe("Header 1");
    expect(listItems.length).toBe(2);
    expect(listItems[0].textContent).toBe("Item 1");
  });

  it("renders code blocks and inline code", () => {
    const markdownText = "Here is `inline code` and a block:\n```js\nconsole.log('hello');\n```";
    const { container } = render(<Markdown source={markdownText} />);

    const inlineCode = container.querySelector("code");
    const preCode = container.querySelector("pre code");

    expect(inlineCode).not.toBeNull();
    expect(preCode).not.toBeNull();
    expect(preCode?.textContent).toContain("console.log('hello');");
  });

  it("sanitizes script tags to prevent XSS", () => {
    const xssMarkdown = `Hello <script>alert("xss")</script>`;
    const { container } = render(<Markdown source={xssMarkdown} />);

    const script = container.querySelector("script");
    expect(script).toBeNull();
    expect(container.textContent).toContain("Hello");
  });
});
