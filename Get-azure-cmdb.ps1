[Hashtable]$sub = @{}
Get-AzSubscription | ForEach-Object { $sub[$_.Id] = $_.Name }

$report = Get-AzureRmResource | Select-Object -Property ResourceID, ResourceName, ResourceGroupName, ResourceType, SubscriptionId, 
@{n = 'SubscriptionName'; e = { $sub[$_.SubscriptionId] } }, 
@{n = 'Tags'; e = { foreach ($i in $_.Tags.GetEnumerator()) 
        { "{0}={1}" -f $i.Key, $i.Value } 
    } 
}

$report | ConvertTo-Csv