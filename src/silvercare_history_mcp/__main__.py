import os

from .server import mcp


def main() -> None:
    """启动 MCP 服务，默认使用 stdio，可通过环境变量切换为 HTTP。"""
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        mcp.run(
            transport="streamable-http",
            host=host,
            port=port,
            stateless_http=True,
        )
    else:
        raise ValueError(
            f"Unsupported MCP_TRANSPORT: {transport}. "
            "Use 'stdio' or 'streamable-http'."
        )


if __name__ == "__main__":
    main()
