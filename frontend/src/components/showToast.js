/**
 * Usage: showToast(title, description, duration, isClosable, status, icon)
 * @param {import("@chakra-ui/react").CreateToastFnReturn} toast
 */
export const configureShowToast = (toast) => {
    const showToast = (title, description, status = 'info', duration = 5000, isClosable = true, icon = null) => {
        if (!["success", "warning", "error", "info"].includes(status)) {
            status = "info"
        }

        const toastConfig = {
            title: title,
            description: description,
            duration: duration,
            isClosable: isClosable,
            status: status
        }
        if (icon != null) {
            toastConfig.icon = icon
        }

        toast.closeAll()
        toast(toastConfig)
    }

    return showToast
}

export default configureShowToast;