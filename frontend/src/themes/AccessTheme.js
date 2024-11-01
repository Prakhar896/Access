import { createSystem, defineConfig, defaultConfig } from "@chakra-ui/react";

const colors = {
    primaryColour: {
        value: "#000000"
    }
}

const AccessTheme = defineConfig({
    theme: {
        tokens: {
            colors,
            fonts: {
                heading: {
                    value: "Roboto, sans-serif"
                }
            }
        }
    }
})

export default createSystem(defaultConfig, AccessTheme);