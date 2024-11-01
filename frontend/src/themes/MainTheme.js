import { Drawer, extendTheme } from "@chakra-ui/react";

const colors = {
    primaryColour: "#000000"
}

const MainTheme = extendTheme({
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
                        bg: 'white',
                        color: 'primaryColour'
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