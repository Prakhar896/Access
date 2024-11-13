/**
 * Usage: showToast(title, description, duration, isClosable, status, icon)
 * @param {import("@chakra-ui/react").CreateToastFnReturn} toast
 */
export default (toast) => {
    const showToast = (title, description, duration = 5000, isClosable = true, status = 'info', icon = null) => {
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