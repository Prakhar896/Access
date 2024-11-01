import { createSystem, defineConfig, defaultConfig } from "@chakra-ui/react";

const colors = {
    primaryColour: {
        value: "#000000"
    }
}

const AccessTheme = {
    theme: {
        tokens: {
            colors,
            fonts: {
                heading: {
                    value: "monospace"
                }
            }
        }
    }
}

export default createSystem(defaultConfig, AccessTheme);