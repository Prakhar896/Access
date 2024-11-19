import { Button, Card, Text } from '@chakra-ui/react'
import React from 'react'

function UploadFileCard({ index, imageName, handleRemoveFile }) {
    return (
        <Card key={index} mb={2} padding={"13px"} display="flex" flexDirection={"row"} justifyContent={"space-between"}>
            <Text fontSize={"15px"} color={"green"} mt={2}>
                {imageName}
            </Text>
            <Button onClick={() => handleRemoveFile(index)} color={'red'}>
                Remove
            </Button>
        </Card>
    )
}

export default UploadFileCard