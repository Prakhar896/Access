import { extendTheme } from "@chakra-ui/react";

const colors = {
    primaryColour: "#000000"
}

const MainTheme = extendTheme({
    initialColorMode: 'dark',
    useSystemColorMode: true,
    colors,
    components: {
        Button: {
            baseStyle: {
                // textTransform: 'uppercase',
                // _focus: {
                //     boxShadow: 'none'
                // }
            },
            variants: {
                Default: {
                    bg: 'primaryColour',
                    borderRadius: '10px',
                    color: 'white',
                    fontWeight: 'bold',
                    _hover: {
                        bg: '#ebedf0',
                        color: 'primaryColour',
                        boxShadow: 'md'
                    }
                }
            }
        },
        Text: {
            baseStyle: {
                fontFamily: 'Ubuntu'
            },
            variants: {
                link: {
                    color: 'grey',
                    textDecoration: 'underline'
                }
            }
        }
    }
})

export default MainTheme;